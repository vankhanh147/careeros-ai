import { API_URL } from "./config";
import { apiFetch } from "./errors";

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
  storage_path?: string | null;
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

export type JobDescriptionUploadPayload = {
  file: File;
  title?: string;
  company?: string;
  source_url?: string;
};

async function jsonRequest<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const response = await apiFetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...init.headers
    }
  }, "Kh\u00f4ng th\u1ec3 x\u1eed l\u00fd d\u1eef li\u1ec7u t\u00e0i li\u1ec7u.");

  return response.json() as Promise<T>;
}

async function emptyRequest(path: string, token: string, init: RequestInit): Promise<void> {
  await apiFetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      ...init.headers
    }
  }, "Kh\u00f4ng th\u1ec3 th\u1ef1c hi\u1ec7n thao t\u00e1c t\u00e0i li\u1ec7u.");
}

export async function uploadResume(token: string, file: File): Promise<Resume> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiFetch(`${API_URL}/api/resumes/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: formData
  }, "Kh\u00f4ng th\u1ec3 upload CV. Vui l\u00f2ng ki\u1ec3m tra file PDF v\u00e0 th\u1eed l\u1ea1i.");

  return response.json() as Promise<Resume>;
}

export function deleteResume(token: string, resumeId: number): Promise<void> {
  return emptyRequest(`/api/resumes/${resumeId}`, token, { method: "DELETE" });
}

export function getMyResumes(token: string): Promise<Resume[]> {
  return jsonRequest<Resume[]>("/api/resumes/me", token);
}

export function createJobDescription(token: string, payload: JobDescriptionPayload): Promise<JobDescription> {
  return jsonRequest<JobDescription>("/api/job-descriptions", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateJobDescription(token: string, jobDescriptionId: number, payload: JobDescriptionPayload): Promise<JobDescription> {
  return jsonRequest<JobDescription>(`/api/job-descriptions/${jobDescriptionId}`, token, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function deleteJobDescription(token: string, jobDescriptionId: number): Promise<void> {
  return emptyRequest(`/api/job-descriptions/${jobDescriptionId}`, token, { method: "DELETE" });
}

export async function uploadJobDescription(token: string, payload: JobDescriptionUploadPayload): Promise<JobDescription> {
  const formData = new FormData();
  formData.append("file", payload.file);
  if (payload.title) formData.append("title", payload.title);
  if (payload.company) formData.append("company", payload.company);
  if (payload.source_url) formData.append("source_url", payload.source_url);

  const response = await apiFetch(`${API_URL}/api/job-descriptions/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: formData
  }, "Kh\u00f4ng th\u1ec3 upload JD. Vui l\u00f2ng d\u00f9ng file PDF ho\u1eb7c TXT d\u01b0\u1edbi 5MB.");

  return response.json() as Promise<JobDescription>;
}

export function getMyJobDescriptions(token: string): Promise<JobDescription[]> {
  return jsonRequest<JobDescription[]>("/api/job-descriptions/me", token);
}
