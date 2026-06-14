import { API_URL } from "./config";
import { apiFetch } from "./errors";

export type CareerProfile = {
  id: number;
  user_id: number;
  target_role: string;
  current_level: string;
  skills: string;
  experience_summary: string;
  projects_summary: string;
  career_goal: string;
  timeline: string;
  created_at: string;
  updated_at: string;
};

export type CareerProfilePayload = {
  target_role: string;
  current_level: string;
  skills: string;
  experience_summary: string;
  projects_summary: string;
  career_goal: string;
  timeline: string;
};

async function request<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const response = await apiFetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...init.headers
    }
  }, "Kh\u00f4ng th\u1ec3 x\u1eed l\u00fd h\u1ed3 s\u01a1 ngh\u1ec1 nghi\u1ec7p.");

  return response.json() as Promise<T>;
}

export function getMyCareerProfile(token: string): Promise<CareerProfile | null> {
  return request<CareerProfile | null>("/api/career-profile/me", token);
}

export function updateMyCareerProfile(token: string, payload: CareerProfilePayload): Promise<CareerProfile> {
  return request<CareerProfile>("/api/career-profile/me", token, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}
