"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { getAnalysisHistory, type MatchAnalysis } from "@/lib/api/analysis";
import {
  answerInterviewQuestion,
  finishInterview,
  getMyInterviews,
  startInterview,
  type InterviewAnswer,
  type InterviewSession
} from "@/lib/api/interviews";
import { useAuth } from "@/lib/auth/AuthContext";
import { FeedbackBlock } from "@/components/FeedbackBlock";

export default function InterviewPage() {
  const router = useRouter();
  const { token, isAuthenticated, isLoading } = useAuth();
  const [analyses, setAnalyses] = useState<MatchAnalysis[]>([]);
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [currentSession, setCurrentSession] = useState<InterviewSession | null>(null);
  const [answerText, setAnswerText] = useState("");
  const [error, setError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isFetching, setIsFetching] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [isAnswering, setIsAnswering] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    let isMounted = true;

    async function loadInterviewData() {
      if (!token) {
        if (isMounted) {
          setIsFetching(false);
        }
        return;
      }

      try {
        setIsFetching(true);
        const [analysisHistory, interviewHistory] = await Promise.all([
          getAnalysisHistory(token),
          getMyInterviews(token)
        ]);
        if (isMounted) {
          setAnalyses(analysisHistory);
          setSessions(interviewHistory);
          setSelectedAnalysisId(analysisHistory[0]?.id ? String(analysisHistory[0].id) : "");
          setCurrentSession(interviewHistory[0] ?? null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Không thể tải dữ liệu Mock Interview. Vui lòng kiểm tra kết nối backend.");
        }
      } finally {
        if (isMounted) {
          setIsFetching(false);
        }
      }
    }

    void loadInterviewData();

    return () => {
      isMounted = false;
    };
  }, [token]);

  const selectedAnalysis = useMemo(
    () => analyses.find((analysis) => String(analysis.id) === selectedAnalysisId),
    [analyses, selectedAnalysisId]
  );

  const currentQuestion = useMemo(
    () => currentSession?.answers.find((answer) => !answer.user_answer) ?? null,
    [currentSession]
  );

  const answeredCount = currentSession?.answers.filter((answer) => answer.user_answer).length ?? 0;
  const canStartInterview = !isStarting;

  async function handleStartInterview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsStarting(true);
    setAnswerText("");

    try {
      const session = await startInterview(token, {
        analysis_id: selectedAnalysisId ? Number(selectedAnalysisId) : undefined,
        target_role: targetRole.trim() || undefined
      });
      setCurrentSession(session);
      setSessions((current) => [session, ...current.filter((item) => item.id !== session.id)].slice(0, 20));
      setStatusMessage("Đã bắt đầu phiên Mock Interview mới.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể bắt đầu Mock Interview. Hãy kiểm tra target role hoặc profile.");
    } finally {
      setIsStarting(false);
    }
  }

  async function handleAnswerQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !currentSession || !currentQuestion) {
      return;
    }
    if (!answerText.trim()) {
      setError("Vui lòng nhập câu trả lời trước khi gửi.");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsAnswering(true);

    try {
      const updated = await answerInterviewQuestion(token, currentSession.id, {
        answer_id: currentQuestion.id,
        user_answer: answerText.trim()
      });
      setCurrentSession(updated);
      setSessions((current) => [updated, ...current.filter((item) => item.id !== updated.id)].slice(0, 20));
      setAnswerText("");
      setStatusMessage("Đã chấm câu trả lời và lưu feedback.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể gửi câu trả lời. Vui lòng thử lại.");
    } finally {
      setIsAnswering(false);
    }
  }

  async function handleFinishInterview() {
    if (!token || !currentSession) {
      return;
    }

    setError("");
    setStatusMessage("");
    setIsFinishing(true);

    try {
      const finished = await finishInterview(token, currentSession.id);
      setCurrentSession(finished);
      setSessions((current) => [finished, ...current.filter((item) => item.id !== finished.id)].slice(0, 20));
      setStatusMessage("Đã hoàn tất phiên Mock Interview.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tổng kết phiên phỏng vấn. Vui lòng thử lại.");
    } finally {
      setIsFinishing(false);
    }
  }

  if (isLoading || isFetching) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">Đang tải Mock Interview...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Mock Interview AI</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/analysis" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              Matching
            </Link>
            <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-4 py-10 sm:px-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Bắt đầu phỏng vấn kỹ thuật</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            MVP này dùng question bank rule-based, ưu tiên skill gap từ analysis nếu có. Không dùng LLM API, không voice/video.
          </p>

          {error ? <p className="mt-5 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
          {statusMessage ? <p className="mt-5 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}

          <form onSubmit={handleStartInterview} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-slate-200">
              Analysis gần đây
              <select
                value={selectedAnalysisId}
                onChange={(event) => setSelectedAnalysisId(event.target.value)}
                className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
              >
                <option value="">Không chọn analysis</option>
                {analyses.map((analysis) => (
                  <option key={analysis.id} value={analysis.id}>
                    #{analysis.id} - Điểm phù hợp {analysis.match_score}% - {new Date(analysis.created_at).toLocaleDateString("vi-VN")}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-sm font-medium text-slate-200">
              Target role tùy chọn
              <input
                type="text"
                value={targetRole}
                onChange={(event) => setTargetRole(event.target.value)}
                placeholder="Ví dụ: Backend Intern, Frontend Developer, AI Engineer"
                className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
              />
            </label>

            {selectedAnalysis ? (
              <div className="rounded-md border border-white/10 bg-slate-950/60 p-4 text-sm leading-6 text-slate-300">
                <p className="font-medium text-slate-100">Analysis đang chọn</p>
                <p className="mt-2 break-words">Skill gap: {selectedAnalysis.skill_gap_summary}</p>
              </div>
            ) : null}

            <button
              type="submit"
              disabled={!canStartInterview}
              className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isStarting ? "Đang tạo phiên phỏng vấn..." : "Bắt đầu phỏng vấn"}
            </button>
          </form>
        </div>

        <div className="min-w-0 space-y-6">
          {currentSession ? (
            <>
              <InterviewSessionPanel
                session={currentSession}
                currentQuestion={currentQuestion}
                answeredCount={answeredCount}
                answerText={answerText}
                setAnswerText={setAnswerText}
                isAnswering={isAnswering}
                isFinishing={isFinishing}
                onAnswer={handleAnswerQuestion}
                onFinish={() => void handleFinishInterview()}
              />
              {currentSession.status === "finished" ? <FeedbackBlock token={token} feedbackType="interview" /> : null}
            </>
          ) : (
            <EmptyInterview />
          )}
        </div>
      </section>

      <section className="mx-auto w-full max-w-6xl px-4 pb-10 sm:px-6">
        <div className="rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Lịch sử phỏng vấn</h2>
          <div className="mt-4 space-y-4">
            {sessions.length === 0 ? (
              <p className="text-sm leading-6 text-slate-400">Chưa có phiên phỏng vấn nào. Bắt đầu phiên đầu tiên bằng form bên trên.</p>
            ) : (
              sessions.map((session) => (
                <InterviewHistoryCard key={session.id} session={session} onSelect={() => setCurrentSession(session)} />
              ))
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

function EmptyInterview() {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-6">
      <h2 className="text-xl font-semibold">Phiên phỏng vấn sẽ hiển thị ở đây</h2>
      <p className="mt-2 text-sm leading-6 text-slate-300">
        Bắt đầu một phiên để nhận khoảng 5 câu hỏi kỹ thuật theo target role và skill gap hiện có.
      </p>
    </div>
  );
}

function InterviewSessionPanel({
  session,
  currentQuestion,
  answeredCount,
  answerText,
  setAnswerText,
  isAnswering,
  isFinishing,
  onAnswer,
  onFinish
}: {
  session: InterviewSession;
  currentQuestion: InterviewAnswer | null;
  answeredCount: number;
  answerText: string;
  setAnswerText: (value: string) => void;
  isAnswering: boolean;
  isFinishing: boolean;
  onAnswer: (event: FormEvent<HTMLFormElement>) => void;
  onFinish: () => void;
}) {
  const isFinished = session.status === "finished";
  const allAnswered = answeredCount === session.answers.length;

  return (
    <article className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">Phiên #{session.id}</p>
          <h2 className="mt-2 break-words text-xl font-semibold">{session.target_role}</h2>
          <p className="mt-1 text-sm text-slate-400">{answeredCount}/{session.answers.length} câu đã trả lời</p>
          <p className="mt-1 text-sm text-slate-400">Trạng thái: {formatInterviewStatus(session.status)}</p>
        </div>
        <div className="shrink-0 rounded-md bg-cyan-300 px-4 py-3 text-center text-slate-950">
          <p className="text-xs font-semibold uppercase tracking-[0.16em]">Điểm</p>
          <p className="mt-1 text-2xl font-bold">{session.score ?? "--"}</p>
        </div>
      </div>

      {session.summary ? <p className="mt-4 break-words rounded-md bg-emerald-300/10 p-3 text-sm leading-6 text-emerald-100">{session.summary}</p> : null}

      {!isFinished && currentQuestion ? (
        <form onSubmit={onAnswer} className="mt-6 space-y-4">
          <div className="rounded-md border border-white/10 bg-slate-950/60 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Câu hỏi tiếp theo</p>
            <p className="mt-2 break-words text-base font-semibold leading-7 text-slate-100">{currentQuestion.question}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {currentQuestion.expected_keywords.map((keyword) => (
                <span key={keyword} className="break-words rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
          <label className="block text-sm font-medium text-slate-200">
            Câu trả lời của bạn
            <textarea
              rows={7}
              value={answerText}
              onChange={(event) => setAnswerText(event.target.value)}
              placeholder="Trả lời theo cấu trúc: khái niệm, cách bạn làm, ví dụ project, trade-off nếu có..."
              className="mt-2 w-full resize-y rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
            />
          </label>
          <button
            type="submit"
            disabled={answerText.trim().length === 0 || isAnswering}
            className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isAnswering ? "Đang chấm câu trả lời..." : "Gửi câu trả lời"}
          </button>
        </form>
      ) : null}

      {!isFinished && allAnswered ? (
        <button
          type="button"
          onClick={onFinish}
          disabled={isFinishing}
          className="mt-6 w-full rounded-md bg-emerald-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isFinishing ? "Đang tổng kết phiên phỏng vấn..." : "Hoàn tất phiên phỏng vấn"}
        </button>
      ) : null}

      <div className="mt-6 space-y-3">
        {session.answers.map((answer, index) => (
          <AnswerCard key={answer.id} answer={answer} index={index} />
        ))}
      </div>
    </article>
  );
}

function AnswerCard({ answer, index }: { answer: InterviewAnswer; index: number }) {
  return (
    <div className="min-w-0 rounded-md border border-white/10 bg-slate-950/60 p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Câu {index + 1}</p>
          <p className="mt-1 break-words text-sm font-semibold leading-6 text-slate-100">{answer.question}</p>
        </div>
        <p className="shrink-0 rounded-md border border-white/10 px-3 py-2 text-sm font-semibold text-cyan-100">
          {answer.score === null ? "Chưa chấm" : `${answer.score}/100`}
        </p>
      </div>
      {answer.user_answer ? <p className="mt-3 whitespace-pre-line break-words text-sm leading-6 text-slate-300">{answer.user_answer}</p> : null}
      {answer.feedback ? <p className="mt-3 break-words rounded-md bg-cyan-300/10 p-3 text-sm leading-6 text-cyan-100">{answer.feedback}</p> : null}
    </div>
  );
}

function InterviewHistoryCard({ session, onSelect }: { session: InterviewSession; onSelect: () => void }) {
  return (
    <article className="min-w-0 rounded-md border border-white/10 bg-slate-950/60 p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h3 className="break-words font-semibold text-slate-100">{session.target_role}</h3>
          <p className="mt-1 text-xs text-slate-500">{new Date(session.created_at).toLocaleString("vi-VN")}</p>
          <p className="mt-1 text-sm text-slate-400">
            Trạng thái: {formatInterviewStatus(session.status)} · Điểm: {formatInterviewScore(session.score)}
          </p>
        </div>
        <button type="button" onClick={onSelect} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
          Xem phiên
        </button>
      </div>
    </article>
  );
}

function formatInterviewStatus(status: string) {
  if (status === "in_progress") {
    return "Đang luyện";
  }
  if (status === "finished") {
    return "Hoàn tất";
  }
  return status || "Chưa có";
}

function formatInterviewScore(score: number | null) {
  return score === null ? "Chưa hoàn thành" : `${score}/100`;
}
