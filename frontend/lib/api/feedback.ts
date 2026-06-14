import { API_URL } from "./config";
import { apiFetch } from "./errors";

export type FeedbackType = "analysis" | "roadmap" | "interview";

export type SubmitFeedbackPayload = {
  feedback_type: FeedbackType;
  useful: boolean;
  comment?: string;
};

export type FeedbackResponse = {
  id: number;
  user_id: number;
  feedback_type: FeedbackType;
  useful: boolean;
  comment: string | null;
  created_at: string;
};

export async function submitFeedback(token: string, payload: SubmitFeedbackPayload): Promise<FeedbackResponse> {
  const response = await apiFetch(`${API_URL}/api/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  }, "Kh\u00f4ng th\u1ec3 g\u1eedi g\u00f3p \u00fd.");

  return response.json() as Promise<FeedbackResponse>;
}
