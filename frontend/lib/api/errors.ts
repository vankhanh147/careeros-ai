export async function getApiErrorMessage(response: Response, fallbackMessage: string): Promise<string> {
  const error = await response.json().catch(() => null) as { detail?: unknown; code?: unknown } | null;
  const code = typeof error?.code === "string" ? error.code : "";
  const detail = typeof error?.detail === "string" ? error.detail : "";

  const byCode: Record<string, string> = {
    EMAIL_ALREADY_REGISTERED: "Email n\u00e0y \u0111\u00e3 \u0111\u01b0\u1ee3c \u0111\u0103ng k\u00fd. H\u00e3y \u0111\u0103ng nh\u1eadp ho\u1eb7c d\u00f9ng email kh\u00e1c.",
    INVALID_CREDENTIALS: "Email ho\u1eb7c m\u1eadt kh\u1ea9u ch\u01b0a \u0111\u00fang. Vui l\u00f2ng ki\u1ec3m tra l\u1ea1i.",
    INVALID_TOKEN: "Phi\u00ean \u0111\u0103ng nh\u1eadp \u0111\u00e3 h\u1ebft h\u1ea1n. Vui l\u00f2ng \u0111\u0103ng nh\u1eadp l\u1ea1i.",
    INACTIVE_USER: "T\u00e0i kho\u1ea3n hi\u1ec7n ch\u01b0a ho\u1ea1t \u0111\u1ed9ng.",
    INVALID_FILE_TYPE: "File kh\u00f4ng \u0111\u00fang \u0111\u1ecbnh d\u1ea1ng. Vui l\u00f2ng ki\u1ec3m tra l\u1ea1i lo\u1ea1i file.",
    FILE_TOO_LARGE: "File v\u01b0\u1ee3t qu\u00e1 gi\u1edbi h\u1ea1n 5MB.",
    RESUME_NOT_FOUND: "Kh\u00f4ng t\u00ecm th\u1ea5y CV \u0111\u00e3 ch\u1ecdn. Vui l\u00f2ng t\u1ea3i l\u1ea1i danh s\u00e1ch ho\u1eb7c upload CV m\u1edbi.",
    JOB_DESCRIPTION_NOT_FOUND: "Kh\u00f4ng t\u00ecm th\u1ea5y JD \u0111\u00e3 ch\u1ecdn. Vui l\u00f2ng t\u1ea3i l\u1ea1i danh s\u00e1ch ho\u1eb7c th\u00eam JD m\u1edbi.",
    ANALYSIS_NOT_FOUND: "Kh\u00f4ng t\u00ecm th\u1ea5y ph\u00e2n t\u00edch \u0111\u00e3 ch\u1ecdn.",
    ROADMAP_INPUT_REQUIRED: "C\u1ea7n c\u00f3 career profile ho\u1eb7c analysis tr\u01b0\u1edbc khi t\u1ea1o roadmap.",
    PROFILE_INCOMPLETE: "H\u00e3y b\u1ed5 sung h\u1ed3 s\u01a1 ngh\u1ec1 nghi\u1ec7p tr\u01b0\u1edbc khi ti\u1ebfp t\u1ee5c.",
    INTERVIEW_SESSION_NOT_FOUND: "Kh\u00f4ng t\u00ecm th\u1ea5y phi\u00ean ph\u1ecfng v\u1ea5n \u0111\u00e3 ch\u1ecdn.",
    INTERVIEW_NO_ANSWERS: "H\u00e3y tr\u1ea3 l\u1eddi \u00edt nh\u1ea5t m\u1ed9t c\u00e2u tr\u01b0\u1edbc khi ho\u00e0n t\u1ea5t ph\u1ecfng v\u1ea5n.",
    VALIDATION_ERROR: "D\u1eef li\u1ec7u ch\u01b0a h\u1ee3p l\u1ec7. Vui l\u00f2ng ki\u1ec3m tra c\u00e1c tr\u01b0\u1eddng b\u1eaft bu\u1ed9c.",
    INTERNAL_SERVER_ERROR: "Backend \u0111ang g\u1eb7p l\u1ed7i t\u1ea1m th\u1eddi. Vui l\u00f2ng th\u1eed l\u1ea1i sau."
  };

  if (code && byCode[code]) {
    return byCode[code];
  }

  const normalizedDetail = detail.toLowerCase();
  if (response.status === 401) {
    return "B\u1ea1n c\u1ea7n \u0111\u0103ng nh\u1eadp l\u1ea1i \u0111\u1ec3 ti\u1ebfp t\u1ee5c.";
  }
  if (response.status === 403) {
    return "B\u1ea1n kh\u00f4ng c\u00f3 quy\u1ec1n th\u1ef1c hi\u1ec7n thao t\u00e1c n\u00e0y.";
  }
  if (response.status === 404) {
    return "Kh\u00f4ng t\u00ecm th\u1ea5y d\u1eef li\u1ec7u c\u1ea7n d\u00f9ng. H\u00e3y t\u1ea3i l\u1ea1i trang ho\u1eb7c ki\u1ec3m tra l\u1ef1a ch\u1ecdn.";
  }
  if (response.status === 409) {
    return "D\u1eef li\u1ec7u \u0111\u00e3 t\u1ed3n t\u1ea1i ho\u1eb7c b\u1ecb tr\u00f9ng. Vui l\u00f2ng ki\u1ec3m tra l\u1ea1i.";
  }
  if (normalizedDetail.includes("file") && normalizedDetail.includes("5mb")) {
    return "File v\u01b0\u1ee3t qu\u00e1 gi\u1edbi h\u1ea1n 5MB.";
  }
  if (normalizedDetail.includes("invalid email") || normalizedDetail.includes("email")) {
    return "Email ch\u01b0a h\u1ee3p l\u1ec7. Vui l\u00f2ng ki\u1ec3m tra l\u1ea1i.";
  }
  if (detail) {
    return detail;
  }

  return fallbackMessage;
}

export function getNetworkErrorMessage(fallbackMessage: string): string {
  return `${fallbackMessage} N\u1ebfu l\u1ed7i v\u1eabn ti\u1ebfp di\u1ec5n, h\u00e3y ki\u1ec3m tra backend ho\u1eb7c k\u1ebft n\u1ed1i m\u1ea1ng.`;
}

export async function apiFetch(input: RequestInfo | URL, init: RequestInit, fallbackMessage: string): Promise<Response> {
  let response: Response;

  try {
    response = await fetch(input, init);
  } catch {
    throw new Error(getNetworkErrorMessage(fallbackMessage));
  }

  if (!response.ok) {
    throw new Error(await getApiErrorMessage(response, fallbackMessage));
  }

  return response;
}
