import { API_URL } from "./config";

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
  const response = await fetch(`${API_URL}/api/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    const message = typeof error?.detail === "string" ? error.detail : "Không thể gửi góp ý. Vui lòng thử lại.";
    throw new Error(message);
  }

  return response.json() as Promise<FeedbackResponse>;
}
