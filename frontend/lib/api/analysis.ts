import { API_URL } from "./config";

export type ScoringBreakdown = {
  skill_score: number;
  keyword_score: number;
  semantic_score: number;
  length_sanity: number;
  final_score: number;
};

export type PrioritizedMissingSkills = {
  high_priority: string[];
  medium_priority: string[];
  low_priority: string[];
};

export type MatchAnalysis = {
  id: number;
  user_id: number;
  resume_id: number;
  job_description_id: number;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  keyword_overlap: string[];
  summary: string;
  suggestions: string[];
  resume_text_preview: string;
  jd_text_preview: string;
  resume_detected_skills: string[];
  jd_detected_skills: string[];
  scoring_breakdown: ScoringBreakdown;
  skill_gap_summary: string;
  prioritized_missing_skills: PrioritizedMissingSkills;
  improvement_plan: string[];
  created_at: string;
  updated_at: string;
};

export type ResumeJobMatchPayload = {
  resume_id: number;
  job_description_id: number;
};

async function analysisRequest<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
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
    const message = typeof error?.detail === "string" ? error.detail : "Không thể xử lý phân tích CV và JD. Vui lòng thử lại.";
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function runResumeJobMatch(token: string, payload: ResumeJobMatchPayload): Promise<MatchAnalysis> {
  return analysisRequest<MatchAnalysis>("/api/analysis/resume-job-match", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getAnalysisHistory(token: string): Promise<MatchAnalysis[]> {
  return analysisRequest<MatchAnalysis[]>("/api/analysis/history", token);
}
