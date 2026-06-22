import { API_URL } from "./config";
import { apiFetch } from "./errors";

export type ScoringBreakdown = {
  skill_score: number;
  keyword_score: number;
  semantic_score: number;
  role_alignment_score: number;
  evidence_score: number;
  length_sanity: number;
  confidence: "high" | "medium" | "low" | string;
  final_score: number;
  resume_role_family?: string;
  jd_role_family?: string;
  resume_role_signals?: Record<string, string[]>;
  jd_role_signals?: Record<string, string[]>;
  resume_stack_groups?: string[];
  jd_stack_groups?: string[];
  critical_skills?: string[];
  role_alignment_notes?: string[];
  evidence_notes?: string[];
};

export type PrioritizedMissingSkills = {
  high_priority: string[];
  medium_priority: string[];
  low_priority: string[];
};

export type ResumeFeedbackItem = {
  title: string;
  message: string;
  why_this_matters: string;
  suggested_edit?: string | null;
};

export type ResumeFeedback = {
  critical_gaps: ResumeFeedbackItem[];
  cv_wording_improvements: ResumeFeedbackItem[];
  suggested_bullet_rewrites: ResumeFeedbackItem[];
  missing_evidence_areas: ResumeFeedbackItem[];
  recommended_next_edits: ResumeFeedbackItem[];
};


export type SemanticInsights = {
  enabled: boolean;
  model_name?: string | null;
  resume_jd_similarity?: number | null;
  confidence: "high" | "medium" | "low" | string;
  notes: string[];
  reason?: string | null;
};

export type HybridEvaluation = {
  enabled: boolean;
  hybrid_score_candidate: number;
  rule_based_score: number;
  semantic_component?: number | null;
  taxonomy_component: number;
  confidence_adjustment: number;
  explanation_notes: string[];
  production_safe: boolean;
};

export type MLEvaluation = {
  enabled: boolean;
  predicted_label?: string | null;
  confidence?: number | null;
  label_probabilities: Record<string, number>;
  model_version?: string | null;
  production_safe: boolean;
  note: string;
  reason?: string | null;
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
  resume_feedback: ResumeFeedback;
  resume_text_preview: string;
  jd_text_preview: string;
  resume_detected_skills: string[];
  jd_detected_skills: string[];
  scoring_breakdown: ScoringBreakdown;
  skill_gap_summary: string;
  prioritized_missing_skills: PrioritizedMissingSkills;
  improvement_plan: string[];
  semantic_insights?: SemanticInsights;
  hybrid_evaluation?: HybridEvaluation;
  ml_evaluation?: MLEvaluation;
  created_at: string;
  updated_at: string;
};

export type ResumeJobMatchPayload = {
  resume_id: number;
  job_description_id: number;
};

async function analysisRequest<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const response = await apiFetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...init.headers
    }
  }, "Kh\u00f4ng th\u1ec3 x\u1eed l\u00fd ph\u00e2n t\u00edch CV v\u00e0 JD.");

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
