import { API_URL } from "./config";
import { apiFetch } from "./errors";

export type RoadmapItem = {
  week: string;
  focus: string;
  skills: string[];
  actions: string[];
  expected_output: string;
  learning_focus?: string | null;
  practice_task?: string | null;
  cv_evidence_output?: string | null;
  interview_prep?: string[];
  priority?: "high" | "medium" | "low" | string;
  completed?: boolean;
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
  const response = await apiFetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...init.headers
    }
  }, "Kh\u00f4ng th\u1ec3 x\u1eed l\u00fd roadmap h\u1ecdc t\u1eadp.");

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

export function updateLatestRoadmapItemCompletion(token: string, itemIndex: number, completed: boolean): Promise<LearningRoadmap> {
  return roadmapRequest<LearningRoadmap>(`/api/roadmaps/latest/items/${itemIndex}/completion`, token, {
    method: "PATCH",
    body: JSON.stringify({ completed })
  });
}
