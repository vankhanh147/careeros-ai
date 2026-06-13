const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type InterviewAnswer = {
  id: number;
  session_id: number;
  question: string;
  expected_keywords: string[];
  user_answer: string | null;
  score: number | null;
  feedback: string | null;
  created_at: string;
};

export type InterviewSession = {
  id: number;
  user_id: number;
  analysis_id: number | null;
  target_role: string;
  status: string;
  score: number | null;
  summary: string | null;
  answers: InterviewAnswer[];
  created_at: string;
  updated_at: string;
};

export type StartInterviewPayload = {
  analysis_id?: number;
  target_role?: string;
};

export type AnswerInterviewPayload = {
  answer_id: number;
  user_answer: string;
};

async function interviewRequest<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
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
    const message = typeof error?.detail === "string" ? error.detail : "Không thể xử lý Mock Interview. Vui lòng thử lại.";
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function startInterview(token: string, payload: StartInterviewPayload): Promise<InterviewSession> {
  return interviewRequest<InterviewSession>("/api/interviews/start", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getMyInterviews(token: string): Promise<InterviewSession[]> {
  return interviewRequest<InterviewSession[]>("/api/interviews/me", token);
}

export function answerInterviewQuestion(token: string, sessionId: number, payload: AnswerInterviewPayload): Promise<InterviewSession> {
  return interviewRequest<InterviewSession>(`/api/interviews/${sessionId}/answer`, token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function finishInterview(token: string, sessionId: number): Promise<InterviewSession> {
  return interviewRequest<InterviewSession>(`/api/interviews/${sessionId}/finish`, token, {
    method: "POST"
  });
}