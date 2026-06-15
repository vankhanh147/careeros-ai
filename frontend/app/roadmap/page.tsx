"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { FeedbackBlock } from "@/components/FeedbackBlock";
import { getAnalysisHistory, type MatchAnalysis } from "@/lib/api/analysis";
import { generateRoadmap, getMyRoadmaps, updateLatestRoadmapItemCompletion, type LearningRoadmap } from "@/lib/api/roadmaps";
import { useAuth } from "@/lib/auth/AuthContext";

const TEXT = {
  priorityHigh: "\u01afu ti\u00ean cao",
  priorityMedium: "\u01afu ti\u00ean trung b\u00ecnh",
  priorityLow: "\u01afu ti\u00ean th\u1ea5p",
  loadError: "Kh\u00f4ng th\u1ec3 t\u1ea3i d\u1eef li\u1ec7u roadmap. Vui l\u00f2ng ki\u1ec3m tra k\u1ebft n\u1ed1i backend.",
  created: "\u0110\u00e3 t\u1ea1o roadmap h\u1ecdc t\u1eadp c\u00e1 nh\u00e2n h\u00f3a.",
  createError: "Kh\u00f4ng th\u1ec3 t\u1ea1o roadmap. H\u00e3y ki\u1ec3m tra profile ho\u1eb7c analysis \u0111\u1ea7u v\u00e0o.",
  loading: "\u0110ang t\u1ea3i roadmap...",
  title: "Roadmap c\u00e1 nh\u00e2n h\u00f3a",
  analysisLink: "Ph\u00e2n t\u00edch CV \u2194 JD",
  createTitle: "T\u1ea1o roadmap h\u1ecdc t\u1eadp",
  intro: "Roadmap MVP \u0111\u01b0\u1ee3c t\u1ea1o b\u1eb1ng rule-based logic t\u1eeb career profile, analysis Resume \u2194 JD, skill gap v\u00e0 timeline. Kh\u00f4ng d\u00f9ng LLM API.",
  recentAnalysis: "Analysis g\u1ea7n \u0111\u00e2y",
  noAnalysisOption: "Kh\u00f4ng ch\u1ecdn analysis - d\u00f9ng career profile c\u01a1 b\u1ea3n",
  matchScore: "\u0110i\u1ec3m ph\u00f9 h\u1ee3p",
  timelineLabel: "Timeline t\u00f9y ch\u1ecdn",
  timelinePlaceholder: "V\u00ed d\u1ee5: 1 tu\u1ea7n, 1 th\u00e1ng, 2 th\u00e1ng",
  selectedAnalysis: "Analysis \u0111ang ch\u1ecdn",
  noAnalysisHint: "N\u1ebfu kh\u00f4ng ch\u1ecdn analysis, backend s\u1ebd d\u00f9ng career profile \u0111\u1ec3 t\u1ea1o roadmap c\u01a1 b\u1ea3n. H\u00e3y c\u1eadp nh\u1eadt profile n\u1ebfu b\u1ea1n ch\u01b0a nh\u1eadp target role, k\u1ef9 n\u0103ng v\u00e0 timeline.",
  generating: "\u0110ang t\u1ea1o roadmap...",
  createButton: "T\u1ea1o roadmap",
  currentRoadmap: "Roadmap hi\u1ec7n t\u1ea1i",
  history: "L\u1ecbch s\u1eed roadmap",
  emptyHistory: "Ch\u01b0a c\u00f3 roadmap n\u00e0o. T\u1ea1o roadmap \u0111\u1ea7u ti\u00ean t\u1eeb profile ho\u1eb7c analysis g\u1ea7n \u0111\u00e2y.",
  emptyTitle: "Roadmap s\u1ebd hi\u1ec3n th\u1ecb \u1edf \u0111\u00e2y",
  emptyBody: "Ch\u1ecdn analysis g\u1ea7n \u0111\u00e2y ho\u1eb7c d\u00f9ng career profile, nh\u1eadp timeline n\u1ebfu c\u1ea7n, r\u1ed3i t\u1ea1o roadmap h\u1ecdc t\u1eadp ng\u1eafn h\u1ea1n c\u00f3 h\u00e0nh \u0111\u1ed9ng c\u1ee5 th\u1ec3 theo t\u1eebng tu\u1ea7n.",
  roadmapLearning: "Roadmap h\u1ecdc t\u1eadp",
  createdAt: "T\u1ea1o l\u00fac",
  steps: "b\u01b0\u1edbc h\u1ecdc t\u1eadp",
  viewRoadmap: "Xem roadmap",
  skills: "K\u1ef9 n\u0103ng",
  noSkillFocus: "T\u1eadp trung v\u00e0o \u0111\u1ed9 kh\u1edbp c\u1ee7a CV v\u00e0 minh ch\u1ee9ng t\u1eeb project.",
  practiceTask: "B\u00e0i th\u1ef1c h\u00e0nh",
  practiceFallback: "T\u1ea1o m\u1ed9t artifact nh\u1ecf ch\u1ee9ng minh tr\u1ecdng t\u00e2m c\u1ee7a tu\u1ea7n n\u00e0y.",
  cvEvidence: "Minh ch\u1ee9ng c\u00f3 th\u1ec3 th\u00eam v\u00e0o CV",
  actions: "H\u00e0nh \u0111\u1ed9ng",
  interviewPrep: "Chu\u1ea9n b\u1ecb ph\u1ecfng v\u1ea5n",
  interviewFallback: "B\u1ea1n \u0111\u00e3 x\u00e2y d\u1ef1ng g\u00ec v\u00e0 c\u00f3 tradeoff k\u1ef9 thu\u1eadt n\u00e0o c\u00f3 th\u1ec3 gi\u1ea3i th\u00edch?",
  expectedOutput: "K\u1ebft qu\u1ea3 mong \u0111\u1ee3i",
  progressSummary: "\u0110\u00e3 ho\u00e0n th\u00e0nh",
  roadmapItems: "m\u1ee5c roadmap",
  completedBadge: "\u0110\u00e3 ho\u00e0n th\u00e0nh",
  incompleteBadge: "Ch\u01b0a ho\u00e0n th\u00e0nh",
  markComplete: "\u0110\u00e1nh d\u1ea5u ho\u00e0n th\u00e0nh",
  markIncomplete: "\u0110\u00e1nh d\u1ea5u ch\u01b0a ho\u00e0n th\u00e0nh",
  updatingProgress: "\u0110ang c\u1eadp nh\u1eadt...",
  progressUpdateError: "Kh\u00f4ng th\u1ec3 c\u1eadp nh\u1eadt tr\u1ea1ng th\u00e1i roadmap. Vui l\u00f2ng th\u1eed l\u1ea1i."
};

const PRIORITY_LABELS: Record<string, string> = {
  high: TEXT.priorityHigh,
  medium: TEXT.priorityMedium,
  low: TEXT.priorityLow
};

export default function RoadmapPage() {
  const router = useRouter();
  const { token, isAuthenticated, isLoading } = useAuth();
  const [analyses, setAnalyses] = useState<MatchAnalysis[]>([]);
  const [roadmaps, setRoadmaps] = useState<LearningRoadmap[]>([]);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState("");
  const [timeline, setTimeline] = useState("");
  const [currentRoadmap, setCurrentRoadmap] = useState<LearningRoadmap | null>(null);
  const [error, setError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isFetching, setIsFetching] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [updatingItemIndex, setUpdatingItemIndex] = useState<number | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    let isMounted = true;

    async function loadRoadmapData() {
      if (!token) {
        if (isMounted) {
          setIsFetching(false);
        }
        return;
      }

      try {
        setIsFetching(true);
        const [analysisHistory, roadmapHistory] = await Promise.all([
          getAnalysisHistory(token),
          getMyRoadmaps(token)
        ]);
        if (isMounted) {
          setAnalyses(analysisHistory);
          setRoadmaps(roadmapHistory);
          setSelectedAnalysisId(analysisHistory[0]?.id ? String(analysisHistory[0].id) : "");
          setCurrentRoadmap(roadmapHistory[0] ?? null);
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

    void loadRoadmapData();

    return () => {
      isMounted = false;
    };
  }, [token]);

  const selectedAnalysis = useMemo(
    () => analyses.find((analysis) => String(analysis.id) === selectedAnalysisId),
    [analyses, selectedAnalysisId]
  );
  const canGenerateRoadmap = !isGenerating;

  async function handleGenerateRoadmap(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsGenerating(true);

    try {
      const payload = {
        analysis_id: selectedAnalysisId ? Number(selectedAnalysisId) : undefined,
        timeline: timeline.trim() || undefined
      };
      const roadmap = await generateRoadmap(token, payload);
      setCurrentRoadmap(roadmap);
      setRoadmaps((current) => [roadmap, ...current.filter((item) => item.id !== roadmap.id)].slice(0, 20));
      setStatusMessage(TEXT.created);
    } catch (err) {
      setError(err instanceof Error ? err.message : TEXT.createError);
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleToggleRoadmapItem(itemIndex: number, completed: boolean) {
    if (!token) {
      router.replace("/login");
      return;
    }

    setError("");
    setStatusMessage("");
    setUpdatingItemIndex(itemIndex);

    try {
      const updatedRoadmap = await updateLatestRoadmapItemCompletion(token, itemIndex, completed);
      setCurrentRoadmap(updatedRoadmap);
      setRoadmaps((current) => current.map((roadmap) => (roadmap.id === updatedRoadmap.id ? updatedRoadmap : roadmap)));
    } catch (err) {
      setError(err instanceof Error ? err.message : TEXT.progressUpdateError);
    } finally {
      setUpdatingItemIndex(null);
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
              {TEXT.analysisLink}
            </Link>
            <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-4 py-10 sm:px-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">{TEXT.createTitle}</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">{TEXT.intro}</p>

          {error ? <p className="mt-5 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
          {statusMessage ? <p className="mt-5 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}

          <form onSubmit={handleGenerateRoadmap} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-slate-200">
              {TEXT.recentAnalysis}
              <select
                value={selectedAnalysisId}
                onChange={(event) => setSelectedAnalysisId(event.target.value)}
                className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
              >
                <option value="">{TEXT.noAnalysisOption}</option>
                {analyses.map((analysis) => (
                  <option key={analysis.id} value={analysis.id}>
                    #{analysis.id} - {TEXT.matchScore} {analysis.match_score}% - {new Date(analysis.created_at).toLocaleDateString("vi-VN")}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-sm font-medium text-slate-200">
              {TEXT.timelineLabel}
              <input
                type="text"
                value={timeline}
                onChange={(event) => setTimeline(event.target.value)}
                placeholder={TEXT.timelinePlaceholder}
                className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
              />
            </label>

            {selectedAnalysis ? (
              <div className="rounded-md border border-white/10 bg-slate-950/60 p-4 text-sm leading-6 text-slate-300">
                <p className="font-medium text-slate-100">{TEXT.selectedAnalysis}</p>
                <p className="mt-2">{TEXT.matchScore}: {selectedAnalysis.match_score}%</p>
                <p className="mt-1 break-words">Skill gap: {selectedAnalysis.skill_gap_summary}</p>
              </div>
            ) : (
              <div className="rounded-md border border-amber-300/20 bg-amber-300/10 p-4 text-sm leading-6 text-amber-100">
                {TEXT.noAnalysisHint}
              </div>
            )}

            <button
              type="submit"
              disabled={!canGenerateRoadmap}
              className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isGenerating ? TEXT.generating : TEXT.createButton}
            </button>
          </form>
        </div>

        <div className="min-w-0 space-y-6">
          {currentRoadmap ? (
            <>
              <RoadmapCard
                roadmap={currentRoadmap}
                title={TEXT.currentRoadmap}
                onToggleItem={currentRoadmap.id === roadmaps[0]?.id ? handleToggleRoadmapItem : undefined}
                updatingItemIndex={updatingItemIndex}
              />
              <FeedbackBlock token={token} feedbackType="roadmap" />
            </>
          ) : <EmptyRoadmap />}
        </div>
      </section>

      <section className="mx-auto w-full max-w-6xl px-4 pb-10 sm:px-6">
        <div className="rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">{TEXT.history}</h2>
          <div className="mt-4 space-y-4">
            {roadmaps.length === 0 ? (
              <p className="text-sm leading-6 text-slate-400">{TEXT.emptyHistory}</p>
            ) : (
              roadmaps.map((roadmap) => (
                <RoadmapCard key={roadmap.id} roadmap={roadmap} compact onSelect={() => setCurrentRoadmap(roadmap)} />
              ))
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

function EmptyRoadmap() {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-6">
      <h2 className="text-xl font-semibold">{TEXT.emptyTitle}</h2>
      <p className="mt-2 text-sm leading-6 text-slate-300">{TEXT.emptyBody}</p>
    </div>
  );
}

function RoadmapCard({ roadmap, title, compact = false, onSelect, onToggleItem, updatingItemIndex }: { roadmap: LearningRoadmap; title?: string; compact?: boolean; onSelect?: () => void; onToggleItem?: (itemIndex: number, completed: boolean) => void; updatingItemIndex?: number | null }) {
  const completedCount = roadmap.items.filter((item) => item.completed === true).length;

  return (
    <article className="min-w-0 rounded-lg border border-white/10 bg-slate-950/60 p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">{title ?? TEXT.roadmapLearning}</p>
          <h3 className="mt-2 break-words text-lg font-semibold text-slate-100">{roadmap.title}</h3>
          <p className="mt-1 text-xs text-slate-500">{TEXT.createdAt} {new Date(roadmap.created_at).toLocaleString("vi-VN")}</p>
        </div>
        <div className="shrink-0 rounded-md bg-cyan-300 px-4 py-3 text-center text-slate-950">
          <p className="text-xs font-semibold uppercase tracking-[0.16em]">Timeline</p>
          <p className="mt-1 text-sm font-bold">{roadmap.timeline}</p>
        </div>
      </div>

      <p className="mt-4 break-words text-sm leading-6 text-slate-300">{roadmap.summary}</p>
      {roadmap.items.length > 0 ? (
        <p className="mt-3 rounded-md border border-cyan-300/20 bg-cyan-300/10 px-3 py-2 text-sm text-cyan-100">
          {TEXT.progressSummary} {completedCount}/{roadmap.items.length} {TEXT.roadmapItems}
        </p>
      ) : null}

      {!compact ? (
        <div className="mt-5 space-y-4">
          {roadmap.items.map((item, itemIndex) => (
            <RoadmapItemCard
              key={`${roadmap.id}-${item.week}-${item.focus}-${itemIndex}`}
              item={item}
              itemIndex={itemIndex}
              onToggleItem={onToggleItem}
              isUpdating={updatingItemIndex === itemIndex}
            />
          ))}
        </div>
      ) : (
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-400">{roadmap.items.length} {TEXT.steps}</p>
          <button type="button" onClick={onSelect} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
            {TEXT.viewRoadmap}
          </button>
        </div>
      )}
    </article>
  );
}

function RoadmapItemCard({ item, itemIndex, onToggleItem, isUpdating = false }: { item: LearningRoadmap["items"][number]; itemIndex: number; onToggleItem?: (itemIndex: number, completed: boolean) => void; isUpdating?: boolean }) {
  const priority = item.priority ?? "medium";
  const isCompleted = item.completed === true;
  const priorityClass = {
    high: "border-red-300/30 bg-red-300/10 text-red-100",
    medium: "border-amber-300/30 bg-amber-300/10 text-amber-100",
    low: "border-slate-300/20 bg-slate-300/10 text-slate-100"
  }[priority] ?? "border-slate-300/20 bg-slate-300/10 text-slate-100";

  return (
    <section className="min-w-0 rounded-md border border-white/10 bg-white/5 p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{item.week}</p>
          <h4 className="mt-1 break-words text-base font-semibold text-slate-100">{item.learning_focus ?? item.focus}</h4>
        </div>
        <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
          <span className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] ${priorityClass}`}>
            {PRIORITY_LABELS[priority] ?? priority}
          </span>
          <span className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold ${isCompleted ? "border-emerald-300/30 bg-emerald-300/10 text-emerald-100" : "border-slate-300/20 bg-slate-300/10 text-slate-300"}`}>
            {isCompleted ? TEXT.completedBadge : TEXT.incompleteBadge}
          </span>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-sm font-semibold text-slate-200">{TEXT.skills}</p>
        {item.skills.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">{TEXT.noSkillFocus}</p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {item.skills.map((skill) => (
              <span key={skill} className="break-words rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs font-medium text-cyan-100">
                {skill}
              </span>
            ))}
          </div>
        )}
      </div>

      <InfoPanel title={TEXT.practiceTask} value={item.practice_task ?? item.actions[0] ?? TEXT.practiceFallback} />
      <InfoPanel title={TEXT.cvEvidence} value={item.cv_evidence_output ?? item.expected_output} tone="emerald" />

      <div className="mt-4">
        <p className="text-sm font-semibold text-slate-200">{TEXT.actions}</p>
        <ul className="mt-2 space-y-2 text-sm leading-6 text-slate-300">
          {item.actions.map((action, actionIndex) => (
            <li key={`${item.week}-action-${actionIndex}`} className="break-words rounded-md border border-white/10 bg-slate-950/70 p-3">{action}</li>
          ))}
        </ul>
      </div>

      <div className="mt-4">
        <p className="text-sm font-semibold text-slate-200">{TEXT.interviewPrep}</p>
        <ul className="mt-2 space-y-2 text-sm leading-6 text-slate-300">
          {(item.interview_prep?.length ? item.interview_prep : [TEXT.interviewFallback]).map((question, questionIndex) => (
            <li key={`${item.week}-question-${questionIndex}`} className="break-words rounded-md border border-white/10 bg-slate-950/70 p-3">{question}</li>
          ))}
        </ul>
      </div>

      <div className="mt-4 rounded-md border border-emerald-300/20 bg-emerald-300/10 p-3 text-sm leading-6 text-emerald-100">
        <span className="font-semibold">{TEXT.expectedOutput}:</span> {item.expected_output}
      </div>

      {onToggleItem ? (
        <button
          type="button"
          disabled={isUpdating}
          onClick={() => onToggleItem(itemIndex, !isCompleted)}
          className="mt-4 w-full rounded-md border border-cyan-300/30 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-300/10 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
        >
          {isUpdating ? TEXT.updatingProgress : isCompleted ? TEXT.markIncomplete : TEXT.markComplete}
        </button>
      ) : null}
    </section>
  );
}

function InfoPanel({ title, value, tone = "slate" }: { title: string; value: string; tone?: "slate" | "emerald" }) {
  const toneClass = tone === "emerald" ? "border-emerald-300/20 bg-emerald-300/10 text-emerald-100" : "border-white/10 bg-slate-950/70 text-slate-300";
  return (
    <div className={`mt-4 rounded-md border p-3 text-sm leading-6 ${toneClass}`}>
      <p className="font-semibold text-slate-100">{title}</p>
      <p className="mt-1 break-words">{value}</p>
    </div>
  );
}
