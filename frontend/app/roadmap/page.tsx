"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { getAnalysisHistory, type MatchAnalysis } from "@/lib/api/analysis";
import { generateRoadmap, getMyRoadmaps, type LearningRoadmap } from "@/lib/api/roadmaps";
import { useAuth } from "@/lib/auth/AuthContext";
import { FeedbackBlock } from "@/components/FeedbackBlock";

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
          setError(err instanceof Error ? err.message : "Không thể tải dữ liệu roadmap. Vui lòng kiểm tra kết nối backend.");
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
      setStatusMessage("Đã tạo roadmap học tập cá nhân hóa.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tạo roadmap. Hãy kiểm tra profile hoặc analysis đầu vào.");
    } finally {
      setIsGenerating(false);
    }
  }

  if (isLoading || isFetching) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">Đang tải roadmap...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Personalized Roadmap</h1>
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
          <h2 className="text-xl font-semibold">Tạo roadmap học tập</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Roadmap MVP được tạo bằng rule-based logic từ career profile, analysis Resume ↔ JD, skill gap và timeline. Không dùng LLM API.
          </p>

          {error ? <p className="mt-5 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
          {statusMessage ? <p className="mt-5 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}

          <form onSubmit={handleGenerateRoadmap} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-slate-200">
              Analysis gần đây
              <select
                value={selectedAnalysisId}
                onChange={(event) => setSelectedAnalysisId(event.target.value)}
                className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
              >
                <option value="">Không chọn analysis - dùng career profile basic</option>
                {analyses.map((analysis) => (
                  <option key={analysis.id} value={analysis.id}>
                    #{analysis.id} - Điểm phù hợp {analysis.match_score}% - {new Date(analysis.created_at).toLocaleDateString("vi-VN")}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-sm font-medium text-slate-200">
              Timeline tùy chọn
              <input
                type="text"
                value={timeline}
                onChange={(event) => setTimeline(event.target.value)}
                placeholder="Ví dụ: 1 tuần, 1 tháng, 2 tháng"
                className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
              />
            </label>

            {selectedAnalysis ? (
              <div className="rounded-md border border-white/10 bg-slate-950/60 p-4 text-sm leading-6 text-slate-300">
                <p className="font-medium text-slate-100">Analysis đang chọn</p>
                <p className="mt-2">Điểm phù hợp: {selectedAnalysis.match_score}%</p>
                <p className="mt-1 break-words">Skill gap: {selectedAnalysis.skill_gap_summary}</p>
              </div>
            ) : (
              <div className="rounded-md border border-amber-300/20 bg-amber-300/10 p-4 text-sm leading-6 text-amber-100">
                Nếu không chọn analysis, backend sẽ dùng career profile để tạo roadmap basic. Hãy cập nhật profile nếu bạn chưa nhập target role, kỹ năng và timeline.
              </div>
            )}

            <button
              type="submit"
              disabled={isGenerating}
              className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isGenerating ? "Đang tạo roadmap..." : "Tạo roadmap"}
            </button>
          </form>
        </div>

        <div className="min-w-0 space-y-6">
          {currentRoadmap ? (
            <>
              <RoadmapCard roadmap={currentRoadmap} title="Roadmap hiện tại" />
              <FeedbackBlock token={token} feedbackType="roadmap" />
            </>
          ) : <EmptyRoadmap />}
        </div>
      </section>

      <section className="mx-auto w-full max-w-6xl px-4 pb-10 sm:px-6">
        <div className="rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Lịch sử roadmap</h2>
          <div className="mt-4 space-y-4">
            {roadmaps.length === 0 ? (
              <p className="text-sm leading-6 text-slate-400">Chưa có roadmap nào. Tạo roadmap đầu tiên từ profile hoặc analysis gần đây.</p>
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
      <h2 className="text-xl font-semibold">Roadmap sẽ hiển thị ở đây</h2>
      <p className="mt-2 text-sm leading-6 text-slate-300">
        Chọn analysis gần đây hoặc dùng career profile, nhập timeline nếu cần, rồi tạo roadmap học tập ngắn hạn có hành động cụ thể theo từng tuần.
      </p>
    </div>
  );
}

function RoadmapCard({ roadmap, title, compact = false, onSelect }: { roadmap: LearningRoadmap; title?: string; compact?: boolean; onSelect?: () => void }) {
  return (
    <article className="min-w-0 rounded-lg border border-white/10 bg-slate-950/60 p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">{title ?? "Roadmap học tập"}</p>
          <h3 className="mt-2 break-words text-lg font-semibold text-slate-100">{roadmap.title}</h3>
          <p className="mt-1 text-xs text-slate-500">Tạo lúc {new Date(roadmap.created_at).toLocaleString("vi-VN")}</p>
        </div>
        <div className="shrink-0 rounded-md bg-cyan-300 px-4 py-3 text-center text-slate-950">
          <p className="text-xs font-semibold uppercase tracking-[0.16em]">Timeline</p>
          <p className="mt-1 text-sm font-bold">{roadmap.timeline}</p>
        </div>
      </div>

      <p className="mt-4 break-words text-sm leading-6 text-slate-300">{roadmap.summary}</p>

      {!compact ? (
        <div className="mt-5 space-y-4">
          {roadmap.items.map((item) => (
            <RoadmapItemCard key={`${roadmap.id}-${item.week}-${item.focus}`} item={item} />
          ))}
        </div>
      ) : (
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-400">{roadmap.items.length} bước học tập</p>
          <button type="button" onClick={onSelect} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
            Xem roadmap
          </button>
        </div>
      )}
    </article>
  );
}

function RoadmapItemCard({ item }: { item: LearningRoadmap["items"][number] }) {
  return (
    <section className="min-w-0 rounded-md border border-white/10 bg-white/5 p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{item.week}</p>
          <h4 className="mt-1 break-words text-base font-semibold text-slate-100">{item.focus}</h4>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-sm font-semibold text-slate-200">Kỹ năng cần học</p>
        {item.skills.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">Tập trung vào CV alignment và project evidence.</p>
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

      <div className="mt-4">
        <p className="text-sm font-semibold text-slate-200">Hành động</p>
        <ul className="mt-2 space-y-2 text-sm leading-6 text-slate-300">
          {item.actions.map((action) => (
            <li key={action} className="break-words rounded-md border border-white/10 bg-slate-950/70 p-3">{action}</li>
          ))}
        </ul>
      </div>

      <div className="mt-4 rounded-md border border-emerald-300/20 bg-emerald-300/10 p-3 text-sm leading-6 text-emerald-100">
        <span className="font-semibold">Kết quả kỳ vọng:</span> {item.expected_output}
      </div>
    </section>
  );
}
