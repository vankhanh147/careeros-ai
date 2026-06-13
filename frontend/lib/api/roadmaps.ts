import { API_URL } from "./config";

export type RoadmapItem = {
  week: string;
  focus: string;
  skills: string[];
  actions: string[];
  expected_output: string;
};

export type LearningRoadmap = {
  id: number;
  user_id: number;
  analysis_id: number | null;
  title: string;
  target_role: string;
  timeline: string;
  items: RoadmapItem[];
  summary: string;
  created_at: string;
  updated_at: string;
};

export type GenerateRoadmapPayload = {
  analysis_id?: number;
  timeline?: string;
};

async function roadmapRequest<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
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
    const message = typeof error?.detail === "string" ? error.detail : "Không thể xử lý roadmap học tập. Vui lòng thử lại.";
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function generateRoadmap(token: string, payload: GenerateRoadmapPayload): Promise<LearningRoadmap> {
  return roadmapRequest<LearningRoadmap>("/api/roadmaps/generate", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getMyRoadmaps(token: string): Promise<LearningRoadmap[]> {
  return roadmapRequest<LearningRoadmap[]>("/api/roadmaps/me", token);
}

export function getRoadmap(token: string, id: number): Promise<LearningRoadmap> {
  return roadmapRequest<LearningRoadmap>(`/api/roadmaps/${id}`, token);
}
