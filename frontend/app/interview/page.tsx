"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { FeedbackBlock } from "@/components/FeedbackBlock";
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

const TEXT = {
  loadError: "Kh\u00f4ng th\u1ec3 t\u1ea3i d\u1eef li\u1ec7u Mock Interview. Vui l\u00f2ng ki\u1ec3m tra k\u1ebft n\u1ed1i backend.",
  started: "\u0110\u00e3 b\u1eaft \u0111\u1ea7u phi\u00ean Mock Interview m\u1edbi.",
  startError: "Kh\u00f4ng th\u1ec3 b\u1eaft \u0111\u1ea7u Mock Interview. H\u00e3y ki\u1ec3m tra vai tr\u00f2 m\u1ee5c ti\u00eau ho\u1eb7c h\u1ed3 s\u01a1 ngh\u1ec1 nghi\u1ec7p.",
  answerRequired: "Vui l\u00f2ng nh\u1eadp c\u00e2u tr\u1ea3 l\u1eddi tr\u01b0\u1edbc khi g\u1eedi.",
  answerSaved: "\u0110\u00e3 ch\u1ea5m c\u00e2u tr\u1ea3 l\u1eddi v\u00e0 l\u01b0u nh\u1eadn x\u00e9t.",
  answerError: "Kh\u00f4ng th\u1ec3 g\u1eedi c\u00e2u tr\u1ea3 l\u1eddi. Vui l\u00f2ng th\u1eed l\u1ea1i.",
  finished: "\u0110\u00e3 ho\u00e0n t\u1ea5t phi\u00ean Mock Interview.",
  finishError: "Kh\u00f4ng th\u1ec3 t\u1ed5ng k\u1ebft phi\u00ean ph\u1ecfng v\u1ea5n. Vui l\u00f2ng th\u1eed l\u1ea1i.",
  loading: "\u0110ang t\u1ea3i Mock Interview...",
  title: "Mock Interview AI",
  matching: "Ph\u00e2n t\u00edch CV \u2194 JD",
  startTitle: "B\u1eaft \u0111\u1ea7u ph\u1ecfng v\u1ea5n k\u1ef9 thu\u1eadt",
  intro: "B\u1ed9 c\u00e2u h\u1ecfi V2 \u01b0u ti\u00ean vai tr\u00f2 m\u1ee5c ti\u00eau, JD, CV, kho\u1ea3ng tr\u1ed1ng k\u1ef9 n\u0103ng v\u00e0 Roadmap hi\u1ec7n c\u00f3.",
  recentAnalysis: "Ph\u00e2n t\u00edch g\u1ea7n \u0111\u00e2y",
  noAnalysis: "Kh\u00f4ng ch\u1ecdn ph\u00e2n t\u00edch",
  matchScore: "\u0110i\u1ec3m ph\u00f9 h\u1ee3p",
  targetRole: "Vai tr\u00f2 m\u1ee5c ti\u00eau t\u00f9y ch\u1ecdn",
  targetPlaceholder: "V\u00ed d\u1ee5: Backend .NET Intern, Frontend React Developer, AI/Data Intern",
  selectedAnalysis: "Ph\u00e2n t\u00edch \u0111ang ch\u1ecdn",
  creating: "\u0110ang t\u1ea1o phi\u00ean ph\u1ecfng v\u1ea5n...",
  startButton: "B\u1eaft \u0111\u1ea7u ph\u1ecfng v\u1ea5n",
  history: "L\u1ecbch s\u1eed ph\u1ecfng v\u1ea5n",
  emptyHistory: "Ch\u01b0a c\u00f3 phi\u00ean ph\u1ecfng v\u1ea5n n\u00e0o. B\u1eaft \u0111\u1ea7u phi\u00ean \u0111\u1ea7u ti\u00ean b\u1eb1ng form b\u00ean tr\u00ean.",
  emptyTitle: "Phi\u00ean ph\u1ecfng v\u1ea5n s\u1ebd hi\u1ec3n th\u1ecb \u1edf \u0111\u00e2y",
  emptyBody: "B\u1eaft \u0111\u1ea7u m\u1ed9t phi\u00ean \u0111\u1ec3 nh\u1eadn 5 c\u00e2u h\u1ecfi theo vai tr\u00f2 m\u1ee5c ti\u00eau, kho\u1ea3ng tr\u1ed1ng k\u1ef9 n\u0103ng v\u00e0 Roadmap hi\u1ec7n c\u00f3.",
  rolePracticing: "Vai tr\u00f2 \u0111ang luy\u1ec7n",
  answered: "c\u00e2u \u0111\u00e3 tr\u1ea3 l\u1eddi",
  status: "Tr\u1ea1ng th\u00e1i",
  score: "\u0110i\u1ec3m",
  nextQuestion: "C\u00e2u h\u1ecfi ti\u1ebfp theo",
  whyAsked: "V\u00ec sao c\u00e2u n\u00e0y \u0111\u01b0\u1ee3c h\u1ecfi",
  relatedSkills: "K\u1ef9 n\u0103ng li\u00ean quan",
  expectedKeywords: "T\u1eeb kh\u00f3a n\u00ean c\u00f3",
  answerLabel: "C\u00e2u tr\u1ea3 l\u1eddi c\u1ee7a b\u1ea1n",
  answerPlaceholder: "Tr\u1ea3 l\u1eddi theo c\u1ea5u tr\u00fac: kh\u00e1i ni\u1ec7m, c\u00e1ch l\u00e0m, v\u00ed d\u1ee5 t\u1eeb d\u1ef1 \u00e1n v\u00e0 l\u1ef1a ch\u1ecdn k\u1ef9 thu\u1eadt n\u1ebfu c\u00f3...",
  grading: "\u0110ang ch\u1ea5m c\u00e2u tr\u1ea3 l\u1eddi...",
  sendAnswer: "G\u1eedi c\u00e2u tr\u1ea3 l\u1eddi",
  finishing: "\u0110ang t\u1ed5ng k\u1ebft phi\u00ean ph\u1ecfng v\u1ea5n...",
  finishButton: "Ho\u00e0n t\u1ea5t phi\u00ean ph\u1ecfng v\u1ea5n",
  feedbackCategory: "Ph\u00e2n lo\u1ea1i nh\u1eadn x\u00e9t",
  betterHint: "G\u1ee3i \u00fd tr\u1ea3 l\u1eddi t\u1ed1t h\u01a1n",
  notGraded: "Ch\u01b0a ch\u1ea5m",
  viewSession: "Xem phi\u00ean",
  inProgress: "\u0110ang luy\u1ec7n",
  done: "Ho\u00e0n t\u1ea5t",
  none: "Ch\u01b0a c\u00f3",
  notFinished: "Ch\u01b0a ho\u00e0n th\u00e0nh"
};

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
          setError(err instanceof Error ? err.message : TEXT.loadError);
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
      setStatusMessage(TEXT.started);
    } catch (err) {
      setError(err instanceof Error ? err.message : TEXT.startError);
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
      setError(TEXT.answerRequired);
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
      setStatusMessage(TEXT.answerSaved);
    } catch (err) {
      setError(err instanceof Error ? err.message : TEXT.answerError);
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
      setStatusMessage(TEXT.finished);
    } catch (err) {
      setError(err instanceof Error ? err.message : TEXT.finishError);
    } finally {
      setIsFinishing(false);
    }
  }

  if (isLoading || isFetching) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">{TEXT.loading}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">{TEXT.title}</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/analysis" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              {TEXT.matching}
            </Link>
            <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-4 py-10 sm:px-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">{TEXT.startTitle}</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">{TEXT.intro}</p>

          {error ? <p className="mt-5 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
          {statusMessage ? <p className="mt-5 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}

          <form onSubmit={handleStartInterview} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-slate-200">
              {TEXT.recentAnalysis}
              <select
                value={selectedAnalysisId}
                onChange={(event) => setSelectedAnalysisId(event.target.value)}
                className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
              >
                <option value="">{TEXT.noAnalysis}</option>
                {analyses.map((analysis) => (
                  <option key={analysis.id} value={analysis.id}>
                    #{analysis.id} - {TEXT.matchScore} {analysis.match_score}% - {new Date(analysis.created_at).toLocaleDateString("vi-VN")}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-sm font-medium text-slate-200">
              {TEXT.targetRole}
              <input
                type="text"
                value={targetRole}
                onChange={(event) => setTargetRole(event.target.value)}
                placeholder={TEXT.targetPlaceholder}
                className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
              />
            </label>

            {selectedAnalysis ? (
              <div className="rounded-md border border-white/10 bg-slate-950/60 p-4 text-sm leading-6 text-slate-300">
                <p className="font-medium text-slate-100">{TEXT.selectedAnalysis}</p>
                <p className="mt-2 break-words">Khoảng trống kỹ năng: {selectedAnalysis.skill_gap_summary}</p>
              </div>
            ) : null}

            <button
              type="submit"
              disabled={!canStartInterview}
              className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isStarting ? TEXT.creating : TEXT.startButton}
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
          <h2 className="text-xl font-semibold">{TEXT.history}</h2>
          <div className="mt-4 space-y-4">
            {sessions.length === 0 ? (
              <p className="text-sm leading-6 text-slate-400">{TEXT.emptyHistory}</p>
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
      <h2 className="text-xl font-semibold">{TEXT.emptyTitle}</h2>
      <p className="mt-2 text-sm leading-6 text-slate-300">{TEXT.emptyBody}</p>
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
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">{TEXT.rolePracticing}</p>
          <h2 className="mt-2 break-words text-xl font-semibold">{session.target_role}</h2>
          <p className="mt-1 text-sm text-slate-400">{answeredCount}/{session.answers.length} {TEXT.answered}</p>
          <p className="mt-1 text-sm text-slate-400">{TEXT.status}: {formatInterviewStatus(session.status)}</p>
        </div>
        <div className="shrink-0 rounded-md bg-cyan-300 px-4 py-3 text-center text-slate-950">
          <p className="text-xs font-semibold uppercase tracking-[0.16em]">{TEXT.score}</p>
          <p className="mt-1 text-2xl font-bold">{session.score ?? "--"}</p>
        </div>
      </div>

      {session.summary ? <p className="mt-4 break-words rounded-md bg-emerald-300/10 p-3 text-sm leading-6 text-emerald-100">{session.summary}</p> : null}

      {!isFinished && currentQuestion ? (
        <form onSubmit={onAnswer} className="mt-6 space-y-4">
          <QuestionPanel answer={currentQuestion} />
          <label className="block text-sm font-medium text-slate-200">
            {TEXT.answerLabel}
            <textarea
              rows={7}
              value={answerText}
              onChange={(event) => setAnswerText(event.target.value)}
              placeholder={TEXT.answerPlaceholder}
              className="mt-2 w-full resize-y rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
            />
          </label>
          <button
            type="submit"
            disabled={answerText.trim().length === 0 || isAnswering}
            className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isAnswering ? TEXT.grading : TEXT.sendAnswer}
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
          {isFinishing ? TEXT.finishing : TEXT.finishButton}
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

function QuestionPanel({ answer }: { answer: InterviewAnswer }) {
  const relatedSkills = answer.related_skills?.length ? answer.related_skills : answer.expected_keywords.slice(0, 4);
  return (
    <div className="rounded-md border border-white/10 bg-slate-950/60 p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{TEXT.nextQuestion}</p>
          <p className="mt-2 break-words text-base font-semibold leading-7 text-slate-100">{answer.question}</p>
        </div>
        {answer.question_category ? (
          <span className="w-fit rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs font-semibold text-cyan-100">
            {formatQuestionCategory(answer.question_category)}
          </span>
        ) : null}
      </div>

      {answer.question_reason ? (
        <div className="mt-4 rounded-md border border-white/10 bg-white/5 p-3 text-sm leading-6 text-slate-300">
          <p className="font-semibold text-slate-100">{TEXT.whyAsked}</p>
          <p className="mt-1 break-words">{answer.question_reason}</p>
        </div>
      ) : null}

      <SkillChips title={TEXT.relatedSkills} items={relatedSkills} />
      <SkillChips title={TEXT.expectedKeywords} items={answer.expected_keywords} muted />
    </div>
  );
}

function SkillChips({ title, items, muted = false }: { title: string; items: string[]; muted?: boolean }) {
  if (items.length === 0) {
    return null;
  }
  return (
    <div className="mt-4">
      <p className="text-sm font-semibold text-slate-200">{title}</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {items.map((item, index) => (
          <span key={`${title}-${item}-${index}`} className={`break-words rounded-full border px-3 py-1 text-xs ${muted ? "border-white/10 bg-white/5 text-slate-300" : "border-cyan-300/20 bg-cyan-300/10 text-cyan-100"}`}>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function AnswerCard({ answer, index }: { answer: InterviewAnswer; index: number }) {
  return (
    <div className="min-w-0 rounded-md border border-white/10 bg-slate-950/60 p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">C?u {index + 1}</p>
          <p className="mt-1 break-words text-sm font-semibold leading-6 text-slate-100">{answer.question}</p>
        </div>
        <p className="shrink-0 rounded-md border border-white/10 px-3 py-2 text-sm font-semibold text-cyan-100">
          {answer.score === null ? TEXT.notGraded : `${answer.score}/100`}
        </p>
      </div>
      {answer.question_reason ? <p className="mt-3 break-words text-xs leading-5 text-slate-500">{TEXT.whyAsked}: {answer.question_reason}</p> : null}
      {answer.user_answer ? <p className="mt-3 whitespace-pre-line break-words text-sm leading-6 text-slate-300">{answer.user_answer}</p> : null}
      {answer.feedback_category ? (
        <p className="mt-3 rounded-md border border-amber-300/20 bg-amber-300/10 p-3 text-sm leading-6 text-amber-100">
          <span className="font-semibold">{TEXT.feedbackCategory}:</span> {answer.feedback_category}
        </p>
      ) : null}
      {answer.feedback ? <p className="mt-3 break-words rounded-md bg-cyan-300/10 p-3 text-sm leading-6 text-cyan-100">{answer.feedback}</p> : null}
      {answer.better_answer_hint ? (
        <p className="mt-3 break-words rounded-md border border-white/10 bg-white/5 p-3 text-sm leading-6 text-slate-300">
          <span className="font-semibold text-slate-100">{TEXT.betterHint}:</span> {answer.better_answer_hint}
        </p>
      ) : null}
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
            {TEXT.status}: {formatInterviewStatus(session.status)} - {TEXT.score}: {formatInterviewScore(session.score)}
          </p>
        </div>
        <button type="button" onClick={onSelect} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
          {TEXT.viewSession}
        </button>
      </div>
    </article>
  );
}

function formatQuestionCategory(category: string) {
  const labels: Record<string, string> = {
    concept: "Concept",
    project_evidence: "Project evidence",
    debugging: "Debugging",
    tradeoff: "Tradeoff",
    behavioral_lite: "Behavioral-lite"
  };
  return labels[category] ?? category;
}

function formatInterviewStatus(status: string) {
  if (status === "in_progress") {
    return TEXT.inProgress;
  }
  if (status === "finished") {
    return TEXT.done;
  }
  return status || TEXT.none;
}

function formatInterviewScore(score: number | null) {
  return score === null ? TEXT.notFinished : `${score}/100`;
}
