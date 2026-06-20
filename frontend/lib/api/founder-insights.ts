import { API_URL } from "./config";
import { apiFetch } from "./errors";

export type FunnelUsage = {
  registered_users: number;
  profile_completed_users: number;
  uploaded_cv_users: number;
  uploaded_jd_users: number;
  generated_analysis_users: number;
  generated_roadmap_users: number;
  started_interview_users: number;
  completed_interview_users: number;
};

export type FeedbackTypeSummary = {
  feedback_type: "analysis" | "roadmap" | "interview" | string;
  total: number;
  useful: number;
  not_useful: number;
  useful_rate: number;
};

export type CommonMissingSkill = {
  skill: string;
  count: number;
};

export type MatchHealthSummary = {
  total_analyses: number;
  average_match_score: number;
  high_confidence_cases: number;
  medium_confidence_cases: number;
  low_confidence_cases: number;
  unknown_confidence_cases: number;
};

export type LearningLoopSummary = {
  users_completing_roadmap_items: number;
  completed_roadmap_items: number;
  users_rerunning_analysis_after_roadmap: number;
};

export type FeedbackLabelSummary = {
  total_feedback_labels: number;
  agreed_labels: number;
  disagreed_labels: number;
};

export type FounderInsights = {
  funnel: FunnelUsage;
  feedback: FeedbackTypeSummary[];
  feedback_labels?: FeedbackLabelSummary;
  common_missing_skills: CommonMissingSkill[];
  match_health: MatchHealthSummary;
  learning_loop: LearningLoopSummary;
};

export async function getFounderInsights(token: string): Promise<FounderInsights> {
  const response = await apiFetch(`${API_URL}/api/founder/insights`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }, "Kh\u00f4ng th\u1ec3 t\u1ea3i founder insights.");

  return response.json() as Promise<FounderInsights>;
}
