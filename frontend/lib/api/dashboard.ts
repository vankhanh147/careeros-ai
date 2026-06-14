import { API_URL } from "./config";
import { apiFetch } from "./errors";

export type DashboardUserInfo = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
};

export type DashboardLatestAnalysis = {
  match_score: number;
  skill_gap_summary: string;
  created_at: string;
};

export type DashboardLatestRoadmap = {
  title: string;
  timeline: string;
  created_at: string;
};

export type DashboardLatestInterview = {
  target_role: string;
  status: string;
  score: number | null;
  created_at: string;
};

export type DashboardSummary = {
  user: DashboardUserInfo;
  has_career_profile: boolean;
  resume_count: number;
  job_description_count: number;
  latest_analysis: DashboardLatestAnalysis | null;
  latest_roadmap: DashboardLatestRoadmap | null;
  latest_interview: DashboardLatestInterview | null;
  recommended_next_actions: string[];
};

export async function getDashboardSummary(token: string): Promise<DashboardSummary> {
  const response = await apiFetch(`${API_URL}/api/dashboard/summary`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }, "Kh\u00f4ng th\u1ec3 t\u1ea3i dashboard.");

  return response.json() as Promise<DashboardSummary>;
}
