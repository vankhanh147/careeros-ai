import json
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from os import getenv
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

logger = logging.getLogger("careeros_api.storage")


@dataclass(frozen=True)
class SupabaseStorageSettings:
    url: str
    service_role_key: str
    bucket: str


class SupabaseStorageClient:
    def __init__(self, settings: SupabaseStorageSettings | None = None) -> None:
        self.settings = settings or _load_settings()

    @property
    def enabled(self) -> bool:
        return self.settings is not None

    def upload_bytes(self, storage_path: str, content: bytes, content_type: str) -> None:
        if not self.settings:
            raise RuntimeError("Supabase Storage is not configured")

        request = Request(
            self._object_url(storage_path),
            data=content,
            method="POST",
            headers={
                **self._auth_headers(),
                "Content-Type": content_type,
                "x-upsert": "false",
            },
        )
        self._send(request, expected_statuses={200, 201})

    def download_bytes(self, storage_path: str) -> bytes:
        if not self.settings:
            raise FileNotFoundError("Supabase Storage is not configured")

        request = Request(self._object_url(storage_path), method="GET", headers=self._auth_headers())
        return self._send(request, expected_statuses={200})

    def create_signed_url(self, storage_path: str, expires_in_seconds: int) -> str:
        if not self.settings:
            raise RuntimeError("Supabase Storage is not configured")
        if expires_in_seconds <= 0:
            raise ValueError("Signed URL expiration must be positive")

        body = json.dumps({"expiresIn": expires_in_seconds}).encode("utf-8")
        request = Request(
            self._sign_url(storage_path),
            data=body,
            method="POST",
            headers={
                **self._auth_headers(),
                "Content-Type": "application/json",
            },
        )
        response_body = self._send(request, expected_statuses={200})
        try:
            payload = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Supabase Storage returned an invalid signed URL response") from exc

        signed_path = payload.get("signedURL") or payload.get("signedUrl")
        if not isinstance(signed_path, str) or not signed_path.strip():
            raise RuntimeError("Supabase Storage did not return a signed URL")
        return self._absolute_signed_url(signed_path)

    def delete_object(self, storage_path: str) -> bool:
        if not self.settings:
            return False

        body = json.dumps({"prefixes": [storage_path]}).encode("utf-8")
        request = Request(
            self._bucket_url(),
            data=body,
            method="DELETE",
            headers={
                **self._auth_headers(),
                "Content-Type": "application/json",
            },
        )
        try:
            self._send(request, expected_statuses={200})
            return True
        except RuntimeError:
            logger.warning("Could not delete Supabase Storage object", extra={"storage_path": storage_path})
            return False

    def _object_url(self, storage_path: str) -> str:
        assert self.settings is not None
        clean_base = self.settings.url.rstrip("/")
        encoded_path = quote(storage_path.strip("/"), safe="/")
        return f"{clean_base}/storage/v1/object/{self.settings.bucket}/{encoded_path}"

    def _sign_url(self, storage_path: str) -> str:
        assert self.settings is not None
        clean_base = self.settings.url.rstrip("/")
        encoded_path = quote(storage_path.strip("/"), safe="/")
        return f"{clean_base}/storage/v1/object/sign/{self.settings.bucket}/{encoded_path}"

    def _absolute_signed_url(self, signed_path: str) -> str:
        assert self.settings is not None
        clean_base = self.settings.url.rstrip("/")
        clean_path = signed_path.strip()
        if clean_path.startswith(("https://", "http://")):
            return clean_path
        if clean_path.startswith("/storage/v1/"):
            return f"{clean_base}{clean_path}"
        if clean_path.startswith("/object/"):
            return f"{clean_base}/storage/v1{clean_path}"
        return f"{clean_base}/{clean_path.lstrip('/')}"

    def _bucket_url(self) -> str:
        assert self.settings is not None
        clean_base = self.settings.url.rstrip("/")
        return f"{clean_base}/storage/v1/object/{self.settings.bucket}"

    def _auth_headers(self) -> dict[str, str]:
        assert self.settings is not None
        return {
            "apikey": self.settings.service_role_key,
            "Authorization": f"Bearer {self.settings.service_role_key}",
        }

    def _send(self, request: Request, expected_statuses: set[int]) -> bytes:
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                if response.status not in expected_statuses:
                    raise RuntimeError(f"Unexpected Supabase Storage status: {response.status}")
                return body
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Supabase Storage request failed: {exc.code} {detail}") from exc
        except URLError as exc:
            raise RuntimeError("Supabase Storage request failed") from exc


def get_storage_service() -> SupabaseStorageClient:
    return SupabaseStorageClient()


def build_resume_storage_path(user_id: int, stored_file_name: str) -> str:
    return f"users/{user_id}/resumes/{stored_file_name}"


def build_job_description_storage_path(user_id: int, stored_file_name: str) -> str:
    return f"users/{user_id}/job-descriptions/{stored_file_name}"


@contextmanager
def readable_file_path(storage_path: str, *, suffix: str = "") -> Iterator[str]:
    local_path = Path(storage_path)
    if local_path.exists() and local_path.is_file():
        yield local_path.as_posix()
        return

    storage = get_storage_service()
    try:
        content = storage.download_bytes(storage_path)
    except RuntimeError as exc:
        raise FileNotFoundError(f"Storage object not found or unreadable: {storage_path}") from exc
    temp_path = ""
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        yield temp_path
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


def _load_settings() -> SupabaseStorageSettings | None:
    url = (getenv("SUPABASE_URL") or "").strip()
    service_role_key = (getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    bucket = (getenv("SUPABASE_STORAGE_BUCKET") or "career-documents").strip()
    if not url or not service_role_key:
        return None
    return SupabaseStorageSettings(url=url, service_role_key=service_role_key, bucket=bucket)
