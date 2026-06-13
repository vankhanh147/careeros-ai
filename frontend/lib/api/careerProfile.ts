const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
        : "Không thể lưu hồ sơ nghề nghiệp. Vui lòng thử lại.";
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getMyCareerProfile(token: string): Promise<CareerProfile | null> {
  return request<CareerProfile | null>("/api/career-profile/me", token);
}

export function updateMyCareerProfile(
  token: string,
  payload: CareerProfilePayload
): Promise<CareerProfile> {
  return request<CareerProfile>("/api/career-profile/me", token, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}
