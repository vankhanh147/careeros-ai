const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Resume = {
  id: number;
  user_id: number;
  file_name: string;
  storage_path: string;
  file_url: string | null;
  extracted_text: string | null;
  created_at: string;
  updated_at: string;
};

export type JobDescription = {
  id: number;
  user_id: number;
  title: string;
  company: string | null;
  content: string;
  source_url: string | null;
  created_at: string;
  updated_at: string;
};

export type JobDescriptionPayload = {
  title: string;
  company?: string;
  content: string;
  source_url?: string;
};

async function jsonRequest<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...init.headers
    }
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    const message =
      typeof error?.detail === "string"
        ? error.detail
        : "Không thể xử lý dữ liệu tài liệu. Vui lòng thử lại.";
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function uploadResume(token: string, file: File): Promise<Resume> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/api/resumes/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: formData
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    const message =
      typeof error?.detail === "string"
        ? error.detail
        : "Không thể upload CV. Vui lòng kiểm tra file PDF và thử lại.";
    throw new Error(message);
  }

  return response.json() as Promise<Resume>;
}

export function getMyResumes(token: string): Promise<Resume[]> {
  return jsonRequest<Resume[]>("/api/resumes/me", token);
}

export function createJobDescription(
  token: string,
  payload: JobDescriptionPayload
): Promise<JobDescription> {
  return jsonRequest<JobDescription>("/api/job-descriptions", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getMyJobDescriptions(token: string): Promise<JobDescription[]> {
  return jsonRequest<JobDescription[]>("/api/job-descriptions/me", token);
}
