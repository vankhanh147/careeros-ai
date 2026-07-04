"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { deleteAnalysis, getAnalysisHistory, runResumeJobMatch, type MatchAnalysis } from "@/lib/api/analysis";
import { getMyJobDescriptions, getMyResumes, type JobDescription, type Resume } from "@/lib/api/documents";
import { useAuth } from "@/lib/auth/AuthContext";
import { FeedbackBlock } from "@/components/FeedbackBlock";

export default function AnalysisPage() {
  const router = useRouter();
  const { token, isAuthenticated, isLoading } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([]);
  const [history, setHistory] = useState<MatchAnalysis[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [selectedJobDescriptionId, setSelectedJobDescriptionId] = useState("");
  const [currentResult, setCurrentResult] = useState<MatchAnalysis | null>(null);
  const [error, setError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isFetching, setIsFetching] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [deletingAnalysisId, setDeletingAnalysisId] = useState<number | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    let isMounted = true;

    async function loadAnalysisData() {
      if (!token) {
        if (isMounted) {
          setIsFetching(false);
        }
        return;
      }

      try {
        setIsFetching(true);
        const [resumeList, jdList, analysisHistory] = await Promise.all([
          getMyResumes(token),
          getMyJobDescriptions(token),
          getAnalysisHistory(token)
        ]);
        if (isMounted) {
          setResumes(resumeList);
          setJobDescriptions(jdList);
          setHistory(analysisHistory);
          setSelectedResumeId(resumeList[0]?.id ? String(resumeList[0].id) : "");
          setSelectedJobDescriptionId(jdList[0]?.id ? String(jdList[0].id) : "");
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Không thể tải dữ liệu phân tích. Vui lòng kiểm tra kết nối backend.");
        }
      } finally {
        if (isMounted) {
          setIsFetching(false);
        }
      }
    }

    void loadAnalysisData();

    return () => {
      isMounted = false;
    };
  }, [token]);

  const selectedResume = useMemo(
    () => resumes.find((resume) => String(resume.id) === selectedResumeId),
    [resumes, selectedResumeId]
  );
  const selectedJobDescription = useMemo(
    () => jobDescriptions.find((job) => String(job.id) === selectedJobDescriptionId),
    [jobDescriptions, selectedJobDescriptionId]
  );
  const canRunAnalysis = Boolean(selectedResumeId && selectedJobDescriptionId) && !isAnalyzing;

  async function handleDeleteAnalysis(analysisId: number) {
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!window.confirm("Bạn có chắc muốn xóa kết quả phân tích này không?")) {
      return;
    }

    setError("");
    setStatusMessage("");
    setDeletingAnalysisId(analysisId);
    try {
      await deleteAnalysis(token, analysisId);
      setHistory((current) => current.filter((item) => item.id !== analysisId));
      setCurrentResult((current) => current?.id === analysisId ? null : current);
      setStatusMessage("Đã xóa kết quả phân tích.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể xóa kết quả phân tích. Vui lòng thử lại.");
    } finally {
      setDeletingAnalysisId(null);
    }
  }

  async function handleRunAnalysis(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!selectedResumeId || !selectedJobDescriptionId) {
      setError("Vui lòng chọn cả CV và JD trước khi phân tích.");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsAnalyzing(true);

    try {
      const result = await runResumeJobMatch(token, {
        resume_id: Number(selectedResumeId),
        job_description_id: Number(selectedJobDescriptionId)
      });
      setCurrentResult(result);
      setHistory((current) => [result, ...current.filter((item) => item.id !== result.id)].slice(0, 20));
      setStatusMessage("Đã phân tích mức độ phù hợp giữa CV và JD.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể chạy Resume ↔ JD Matching. Vui lòng thử lại.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  if (isLoading || isFetching) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">Đang tải dữ liệu phân tích...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Resume ↔ JD Matching</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/documents" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              CV & JD
            </Link>
            <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-4 py-10 sm:px-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div id="analysis-form" className="min-w-0 scroll-mt-6 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Chọn dữ liệu phân tích</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Hệ thống kết hợp kỹ năng, từ khóa, vai trò và bằng chứng trong CV để đánh giá mức độ phù hợp với JD.
          </p>

          {resumes.length === 0 || jobDescriptions.length === 0 ? (
            <div className="mt-6 rounded-md border border-amber-300/20 bg-amber-300/10 p-4 text-sm leading-6 text-amber-100">
              Bạn cần có ít nhất một CV PDF và một JD trước khi chạy phân tích.
              <div className="mt-4">
                <Link href="/documents" className="font-semibold text-amber-50 underline underline-offset-4">
                  Tải CV lên hoặc thêm JD
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleRunAnalysis} className="mt-6 space-y-4">
              <label className="block text-sm font-medium text-slate-200">
                CV PDF
                <select
                  value={selectedResumeId}
                  onChange={(event) => setSelectedResumeId(event.target.value)}
                  className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                >
                  {resumes.map((resume) => (
                    <option key={resume.id} value={resume.id}>{resume.file_name}</option>
                  ))}
                </select>
              </label>

              <label className="block text-sm font-medium text-slate-200">
                JD mục tiêu
                <select
                  value={selectedJobDescriptionId}
                  onChange={(event) => setSelectedJobDescriptionId(event.target.value)}
                  className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                >
                  {jobDescriptions.map((job) => (
                    <option key={job.id} value={job.id}>{job.title}{job.company ? ` - ${job.company}` : ""}</option>
                  ))}
                </select>
              </label>

              <div className="rounded-md border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-300">
                <p className="font-medium text-slate-100">Dữ liệu đang chọn</p>
                <p className="mt-2 break-words">CV: {selectedResume?.file_name ?? "Chưa chọn"}</p>
                <p className="mt-1 break-words">JD: {selectedJobDescription?.title ?? "Chưa chọn"}</p>
              </div>

              <button
                type="submit"
                disabled={!canRunAnalysis}
                className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isAnalyzing ? "Đang phân tích..." : "Phân tích mức độ phù hợp"}
              </button>
            </form>
          )}
        </div>

        <div className="min-w-0 space-y-6">
          {error ? <p className="rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
          {statusMessage ? <p className="rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}
          {currentResult ? (
            <>
              <AnalysisResultCard analysis={currentResult} title="Kết quả vừa tạo" />
              <FeedbackBlock token={token} feedbackType="analysis" />
            </>
          ) : <EmptyResult />}
        </div>
      </section>

      <section className="mx-auto w-full max-w-6xl px-4 pb-10 sm:px-6">
        <div className="rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Lịch sử phân tích gần đây</h2>
          <div className="mt-4 space-y-4">
            {history.length === 0 ? (
              <p className="text-sm leading-6 text-slate-400">Chưa có kết quả phân tích. Hãy chạy Resume ↔ JD Matching để xem điểm phù hợp, khoảng trống kỹ năng và gợi ý cải thiện.</p>
            ) : (
              history.map((analysis) => (
                <AnalysisResultCard
                  key={analysis.id}
                  analysis={analysis}
                  compact
                  onDelete={handleDeleteAnalysis}
                  isDeleting={deletingAnalysisId === analysis.id}
                />
              ))
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

function EmptyResult() {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-6">
      <h2 className="text-xl font-semibold">Kết quả phân tích</h2>
      <p className="mt-2 text-sm leading-6 text-slate-300">
        Chọn một CV và một JD để xem điểm phù hợp, kỹ năng đã khớp, khoảng trống kỹ năng và dữ liệu hệ thống đã đọc.
      </p>
    </div>
  );
}

function AnalysisResultCard({
  analysis,
  title = "Kết quả phân tích",
  compact = false,
  onDelete,
  isDeleting = false
}: {
  analysis: MatchAnalysis;
  title?: string;
  compact?: boolean;
  onDelete?: (analysisId: number) => void;
  isDeleting?: boolean;
}) {
  const scoreMeaning = getScoreMeaning(analysis.match_score);
  const criticalGapCount = analysis.prioritized_missing_skills.high_priority.length;

  return (
    <article className="min-w-0 rounded-lg border border-white/10 bg-slate-950/60 p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
          <p className="mt-1 text-xs text-slate-500">{new Date(analysis.created_at).toLocaleString("vi-VN")}</p>
          {compact && onDelete ? (
            <button
              type="button"
              disabled={isDeleting}
              onClick={() => onDelete(analysis.id)}
              className="mt-3 rounded-md border border-red-300/20 px-3 py-1.5 text-xs font-semibold text-red-200 transition hover:bg-red-300/10 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isDeleting ? "Đang xóa..." : "Xóa"}
            </button>
          ) : null}
        </div>
        <div className="shrink-0 rounded-md bg-cyan-300 px-4 py-3 text-center text-slate-950">
          <p className="text-xs font-semibold uppercase tracking-[0.16em]">Điểm phù hợp</p>
          <p className="mt-1 text-2xl font-bold">{analysis.match_score}%</p>
          <p className="mt-1 text-xs font-semibold">{scoreMeaning.label}</p>
        </div>
      </div>

      <div className="mt-4 rounded-md border border-cyan-300/15 bg-cyan-300/5 p-4">
        <p className="break-words text-sm leading-6 text-slate-200">{formatAnalysisText(analysis.summary)}</p>
        <p className="mt-2 text-sm leading-6 text-cyan-100">
          {criticalGapCount > 0
            ? `Nên ưu tiên cải thiện ${criticalGapCount} kỹ năng quan trọng trước khi ứng tuyển.`
            : scoreMeaning.guidance}
        </p>
      </div>

      <SkillGapSection analysis={analysis} compact={compact} />

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <SkillList title="Kỹ năng đã khớp" items={analysis.matched_skills} emptyText="Chưa phát hiện kỹ năng khớp rõ ràng." tone="positive" />
        <SkillList title="Kỹ năng còn thiếu" items={analysis.missing_skills} emptyText="Chưa phát hiện khoảng trống kỹ năng lớn." tone="warning" />
      </div>

      {!compact ? (
        <>
          <AnalysisSection title="Từ khóa trùng khớp" defaultOpen={false}>
            <TagList items={analysis.keyword_overlap} emptyText="Chưa có từ khóa trùng khớp đáng kể." />
          </AnalysisSection>
          <ResumeFeedbackSection feedback={analysis.resume_feedback} />
          <AnalysisSection title="Gợi ý cải thiện tiếp theo">
            <ul className="space-y-2 text-sm leading-6 text-slate-300">
              {analysis.suggestions.map((suggestion, index) => (
                <li key={`${index}-${suggestion}`} className="break-words rounded-md border border-white/10 bg-white/5 p-3">
                  {formatAnalysisText(suggestion)}
                </li>
              ))}
            </ul>
          </AnalysisSection>
          <DebugPreview analysis={analysis} />
          <NextActions />
        </>
      ) : null}
    </article>
  );
}

function AnalysisSection({ title, badge, defaultOpen = true, children }: { title: string; badge?: string; defaultOpen?: boolean; children: React.ReactNode }) {
  return (
    <details open={defaultOpen} className="group mt-5 rounded-lg border border-white/10 bg-white/5">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 p-4 text-sm font-semibold text-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
        <span className="flex min-w-0 flex-wrap items-center gap-2">
          {title}
          {badge ? <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2 py-0.5 text-xs font-medium text-cyan-100">{badge}</span> : null}
        </span>
        <span className="shrink-0 text-xs text-slate-500 group-open:hidden">Mở</span>
        <span className="hidden shrink-0 text-xs text-slate-500 group-open:inline">Thu gọn</span>
      </summary>
      <div className="border-t border-white/10 p-4">{children}</div>
    </details>
  );
}

function ResumeFeedbackSection({ feedback }: { feedback?: MatchAnalysis["resume_feedback"] }) {
  if (!feedback) return null;

  const groups = [
    { title: "Khoảng trống quan trọng", priority: "Quan trọng", items: feedback.critical_gaps },
    { title: "Minh chứng còn thiếu", priority: "Quan trọng", items: feedback.missing_evidence_areas },
    { title: "Cải thiện cách diễn đạt", priority: "Nên cải thiện", items: feedback.cv_wording_improvements },
    { title: "Gợi ý viết lại nội dung", priority: "Nên cải thiện", items: feedback.suggested_bullet_rewrites },
    { title: "Chỉnh sửa nên làm tiếp theo", priority: "Có thể bổ sung", items: feedback.recommended_next_edits }
  ].filter((group) => group.items.length > 0);

  if (groups.length === 0) return null;

  return (
    <details open className="group mt-5 rounded-lg border border-emerald-300/20 bg-emerald-300/5">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 p-5 text-base font-semibold text-emerald-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
        Gợi ý cải thiện CV
        <span className="text-xs text-emerald-200/70 group-open:hidden">Mở</span>
        <span className="hidden text-xs text-emerald-200/70 group-open:inline">Thu gọn</span>
      </summary>
      <div className="border-t border-emerald-300/10 p-5 pt-4">
        <p className="text-sm leading-6 text-slate-300">
          Gợi ý dựa trên CV và JD hệ thống đã đọc, sử dụng quy tắc có thể giải thích. Chỉ thêm nội dung phản ánh đúng kinh nghiệm thực tế của bạn.
        </p>
        <div className="mt-5 space-y-5">
          {groups.map((group) => (
            <div key={group.title} className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h5 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-300">{group.title}</h5>
                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-slate-400">{group.priority}</span>
              </div>
              <div className="mt-3 grid gap-3">
                {group.items.map((item, itemIndex) => (
                  <div key={`${group.title}-${itemIndex}-${item.title}`} className="rounded-md border border-white/10 bg-slate-950/70 p-4 text-sm leading-6 text-slate-300">
                    <p className="font-semibold text-slate-100">{formatAnalysisText(item.title)}</p>
                    <p className="mt-2 break-words">{formatAnalysisText(item.message)}</p>
                    <p className="mt-2 break-words text-slate-400">
                      <span className="font-medium text-slate-300">Vì sao điều này quan trọng:</span> {formatAnalysisText(item.why_this_matters)}
                    </p>
                    {item.suggested_edit ? (
                      <p className="mt-2 break-words rounded-md border border-emerald-300/15 bg-emerald-300/5 p-3 text-emerald-100">
                        <span className="font-medium">Gợi ý chỉnh sửa:</span> {formatAnalysisText(item.suggested_edit)}
                      </p>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </details>
  );
}

function SkillGapSection({ analysis, compact }: { analysis: MatchAnalysis; compact: boolean }) {
  const prioritized = analysis.prioritized_missing_skills;
  return (
    <details open className="group mt-5 rounded-lg border border-white/10 bg-white/5">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 p-5 text-base font-semibold text-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
        Khoảng trống kỹ năng
        <span className="text-xs text-slate-500 group-open:hidden">Mở</span>
        <span className="hidden text-xs text-slate-500 group-open:inline">Thu gọn</span>
      </summary>
      <div className="border-t border-white/10 p-5 pt-4">
        <p className="break-words text-sm leading-6 text-slate-300">{formatAnalysisText(analysis.skill_gap_summary)}</p>
        <div className="mt-5 grid gap-4 lg:grid-cols-3">
          <PriorityList title="Ưu tiên cao" items={prioritized.high_priority} tone="high" />
          <PriorityList title="Ưu tiên trung bình" items={prioritized.medium_priority} tone="medium" />
          <PriorityList title="Ưu tiên thấp" items={prioritized.low_priority} tone="low" />
        </div>
        {!compact ? (
          <div className="mt-5">
            <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Kế hoạch cải thiện ngắn hạn</h5>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">
              {analysis.improvement_plan.map((action, index) => (
                <li key={`${index}-${action}`} className="break-words rounded-md border border-white/10 bg-slate-950/60 p-3">{formatAnalysisText(action)}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </details>
  );
}

function PriorityList({ title, items, tone }: { title: string; items: string[]; tone: "high" | "medium" | "low" }) {
  const toneClass = { high: "text-red-200", medium: "text-amber-200", low: "text-slate-200" }[tone];
  return (
    <div className="min-w-0">
      <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{title}</h5>
      <div className="mt-3">
        {items.length === 0 ? <p className="text-sm text-slate-500">Chưa có.</p> : <TagList items={items} className={toneClass} />}
      </div>
    </div>
  );
}

function DebugPreview({ analysis }: { analysis: MatchAnalysis }) {
  return (
    <>
      <AnalysisSection title="Dữ liệu hệ thống đã đọc được" defaultOpen={false}>
        <p className="text-sm leading-6 text-slate-300">Kiểm tra nhanh nội dung hệ thống đã đọc từ CV và JD trước khi sử dụng kết quả.</p>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <PreviewBox title="Nội dung CV đã đọc" text={analysis.resume_text_preview} />
          <PreviewBox title="Nội dung JD đã đọc" text={analysis.jd_text_preview} />
        </div>
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          <SkillList title="Kỹ năng phát hiện trong CV" items={analysis.resume_detected_skills} emptyText="Chưa phát hiện kỹ năng trong CV." tone="positive" />
          <SkillList title="Kỹ năng phát hiện trong JD" items={analysis.jd_detected_skills} emptyText="Chưa phát hiện kỹ năng trong JD." tone="warning" />
        </div>
      </AnalysisSection>

      <AnalysisSection title="Chi tiết cách chấm điểm" badge="Nội bộ" defaultOpen={false}>
        <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <ScoreItem label="Điểm kỹ năng" value={analysis.scoring_breakdown.skill_score} />
          <ScoreItem label="Điểm từ khóa" value={analysis.scoring_breakdown.keyword_score} />
          <ScoreItem label="Điểm ngữ nghĩa" value={analysis.scoring_breakdown.semantic_score} />
          <ScoreItem label="Độ khớp vai trò" value={analysis.scoring_breakdown.role_alignment_score} />
          <ScoreItem label="Điểm minh chứng" value={analysis.scoring_breakdown.evidence_score} />
          <ScoreItem label="Độ đầy đủ dữ liệu" value={analysis.scoring_breakdown.length_sanity} />
          <TextItem label="Độ tin cậy" value={formatConfidence(analysis.scoring_breakdown.confidence)} />
          <ScoreItem label="Điểm cuối cùng" value={analysis.scoring_breakdown.final_score} />
        </dl>
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          <InfoBlock title="Vai trò và stack đã phát hiện" lines={[
            `CV: ${formatRole(analysis.scoring_breakdown.resume_role_family)}`,
            `JD: ${formatRole(analysis.scoring_breakdown.jd_role_family)}`,
            `Stack CV: ${(analysis.scoring_breakdown.resume_stack_groups ?? []).join(", ") || "Chưa rõ"}`,
            `Stack JD: ${(analysis.scoring_breakdown.jd_stack_groups ?? []).join(", ") || "Chưa rõ"}`
          ]} />
          <InfoBlock title="Giải thích cách chấm điểm" lines={[
            ...((analysis.scoring_breakdown.role_alignment_notes ?? []).slice(0, 4)),
            ...((analysis.scoring_breakdown.evidence_notes ?? []).slice(0, 4))
          ].map(formatAnalysisText)} />
        </div>
        <div className="mt-5">
          <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Kỹ năng quan trọng trong JD</h5>
          <div className="mt-3"><TagList items={analysis.scoring_breakdown.critical_skills ?? []} emptyText="Chưa phát hiện kỹ năng quan trọng rõ ràng." /></div>
        </div>
      </AnalysisSection>

      <SemanticInsightBlock insight={analysis.semantic_insights} />
      <HybridEvaluationBlock evaluation={analysis.hybrid_evaluation} semanticEnabled={Boolean(analysis.semantic_insights?.enabled)} />
      <MLEvaluationBlock evaluation={analysis.ml_evaluation} />
    </>
  );
}

function SemanticInsightBlock({ insight }: { insight?: MatchAnalysis["semantic_insights"] }) {
  if (!insight) return null;
  const similarity = typeof insight.resume_jd_similarity === "number" ? `${Math.round(insight.resume_jd_similarity * 100)}%` : "Chưa có";
  return (
    <AnalysisSection title="Tín hiệu Semantic" badge="Thử nghiệm" defaultOpen={false}>
      <p className="text-sm leading-6 text-slate-300">Tín hiệu ngữ nghĩa chạy song song để đánh giá nội bộ, không thay đổi điểm phù hợp chính.</p>
      <dl className="mt-4 grid gap-3 sm:grid-cols-3">
        <TextItem label="Trạng thái" value={insight.enabled ? "Đang bật" : "Đang tắt"} />
        <TextItem label="Độ tương đồng" value={similarity} />
        <TextItem label="Độ tin cậy" value={formatConfidence(insight.confidence)} />
      </dl>
      {insight.reason ? <p className="mt-3 break-words text-sm text-slate-400">Lý do: {formatAnalysisText(insight.reason)}</p> : null}
      {insight.notes.length > 0 ? <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">{insight.notes.map((note, index) => <li key={`${index}-${note}`}>{formatAnalysisText(note)}</li>)}</ul> : null}
    </AnalysisSection>
  );
}

function HybridEvaluationBlock({ evaluation, semanticEnabled }: { evaluation?: MatchAnalysis["hybrid_evaluation"]; semanticEnabled: boolean }) {
  if (!evaluation) return null;
  return (
    <AnalysisSection title="Hybrid evaluation" badge="Đánh giá nội bộ" defaultOpen={false}>
      <p className="text-sm leading-6 text-slate-300">Điểm thử nghiệm này chưa thay thế điểm phù hợp chính và không ảnh hưởng kết quả người dùng.</p>
      <dl className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <TextItem label="Điểm production hiện tại" value={`${evaluation.rule_based_score}%`} />
        <TextItem label="Điểm hybrid thử nghiệm" value={`${evaluation.hybrid_score_candidate}%`} />
        <TextItem label="Semantic" value={semanticEnabled ? "Đang bật" : "Đang tắt"} />
        <TextItem label="Thành phần taxonomy" value={`${evaluation.taxonomy_component}%`} />
      </dl>
      {evaluation.explanation_notes.length > 0 ? <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">{evaluation.explanation_notes.map((note, index) => <li key={`${index}-${note}`}>{formatAnalysisText(note)}</li>)}</ul> : null}
    </AnalysisSection>
  );
}

function MLEvaluationBlock({ evaluation }: { evaluation?: MatchAnalysis["ml_evaluation"] }) {
  if (!evaluation) return null;
  const confidence = typeof evaluation.confidence === "number" ? `${Math.round(evaluation.confidence * 100)}%` : "Chưa có";
  return (
    <AnalysisSection title="Đánh giá ML" badge="Thử nghiệm" defaultOpen={false}>
      <p className="text-sm leading-6 text-slate-300">Dự đoán ML chỉ phục vụ đánh giá nội bộ, chưa thay thế điểm phù hợp chính.</p>
      <dl className="mt-4 grid gap-3 sm:grid-cols-3">
        <TextItem label="Nhãn dự đoán" value={formatPredictionLabel(evaluation.predicted_label)} />
        <TextItem label="Độ tự tin" value={confidence} />
        <TextItem label="Phiên bản mô hình" value={evaluation.model_version ?? "Chưa có"} />
      </dl>
      <p className="mt-3 break-words text-sm text-slate-400">{formatAnalysisText(evaluation.note)}</p>
      {evaluation.reason ? <p className="mt-2 break-words text-sm text-slate-500">Lý do: {formatAnalysisText(evaluation.reason)}</p> : null}
    </AnalysisSection>
  );
}

function NextActions() {
  const actions = [
    { href: "/roadmap", label: "Tạo Roadmap" },
    { href: "/interview", label: "Luyện Mock Interview" },
    { href: "/documents", label: "Quản lý CV/JD" }
  ];
  return (
    <section className="mt-6 rounded-lg border border-cyan-300/20 bg-cyan-300/5 p-5">
      <h4 className="text-base font-semibold text-cyan-100">Bước tiếp theo</h4>
      <p className="mt-2 text-sm leading-6 text-slate-300">Dùng kết quả này để cải thiện hồ sơ hoặc tiếp tục luồng luyện tập phù hợp.</p>
      <div className="mt-4 flex flex-wrap gap-3">
        {actions.map((action) => <Link key={action.href} href={action.href} className="rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200">{action.label}</Link>)}
        <a href="#analysis-form" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:bg-white/10">Phân tích JD khác</a>
      </div>
    </section>
  );
}

function PreviewBox({ title, text }: { title: string; text: string }) {
  return (
    <div className="min-w-0">
      <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{title}</h5>
      <p className="mt-3 max-h-40 overflow-auto break-words rounded-md border border-white/10 bg-slate-950/80 p-3 text-sm leading-6 text-slate-300">{text || "Chưa có nội dung xem trước."}</p>
    </div>
  );
}

function ScoreItem({ label, value }: { label: string; value: number }) {
  return <div className="min-w-0 rounded-md border border-white/10 bg-slate-950/70 p-3"><dt className="break-words text-xs uppercase tracking-[0.16em] text-slate-500">{label}</dt><dd className="mt-2 text-lg font-semibold text-slate-100">{value}</dd></div>;
}

function TextItem({ label, value }: { label: string; value: string }) {
  return <div className="min-w-0 rounded-md border border-white/10 bg-slate-950/70 p-3"><dt className="break-words text-xs uppercase tracking-[0.16em] text-slate-500">{label}</dt><dd className="mt-2 break-words text-base font-semibold text-slate-100">{value}</dd></div>;
}

function InfoBlock({ title, lines }: { title: string; lines: string[] }) {
  const visibleLines = lines.filter(Boolean);
  return (
    <div className="min-w-0 rounded-md border border-white/10 bg-slate-950/70 p-4">
      <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{title}</h5>
      {visibleLines.length === 0 ? <p className="mt-3 text-sm text-slate-500">Chưa có tín hiệu rõ ràng.</p> : <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">{visibleLines.map((line, index) => <li key={`${index}-${line}`} className="break-words">{line}</li>)}</ul>}
    </div>
  );
}

function getScoreMeaning(score: number) {
  if (score < 35) return { label: "Chưa phù hợp", guidance: "Nên xem lại vai trò mục tiêu và các kỹ năng cốt lõi trước khi ứng tuyển." };
  if (score < 55) return { label: "Cần cải thiện nhiều", guidance: "Hãy ưu tiên các khoảng trống quan trọng và bổ sung minh chứng thật trong CV." };
  if (score < 75) return { label: "Khá phù hợp", guidance: "CV đã có nền tảng liên quan; nên làm rõ minh chứng và các kỹ năng còn thiếu." };
  if (score < 90) return { label: "Phù hợp tốt", guidance: "Hồ sơ có độ khớp tốt; hãy rà lại cách diễn đạt và chuẩn bị phỏng vấn theo JD." };
  return { label: "Rất phù hợp", guidance: "Hồ sơ có độ khớp rất cao; vẫn nên kiểm tra tính chính xác của minh chứng trước khi ứng tuyển." };
}

function formatConfidence(confidence?: string) {
  if (confidence === "high") return "Cao";
  if (confidence === "low") return "Thấp";
  if (confidence === "medium") return "Trung bình";
  return "Chưa xác định";
}

function formatPredictionLabel(label?: string | null) {
  return ({ good: "Phù hợp tốt", medium: "Phù hợp trung bình", weak: "Phù hợp thấp", mismatch: "Không phù hợp" } as Record<string, string>)[label ?? ""] ?? "Chưa có";
}

function formatRole(role?: string | null) {
  if (!role) return "Phát triển phần mềm nói chung";
  return ({ backend: "Backend", frontend: "Frontend", fullstack: "Fullstack", "ai/data": "AI / Data", mobile: "Mobile", devops: "DevOps", "general software": "Phát triển phần mềm nói chung" } as Record<string, string>)[role] ?? role;
}

function formatAnalysisText(value?: string | null) {
  if (!value) return "";
  const exact: Record<string, string> = {
    "semantic model disabled": "Mô hình semantic đang tắt.",
    "semantic model unavailable": "Mô hình semantic hiện không khả dụng.",
    "Role alignment needs to be clearer": "Cần làm rõ mức độ phù hợp với vai trò",
    "A role mismatch can make relevant transferable work harder for recruiters to notice.": "Khác biệt vai trò có thể khiến nhà tuyển dụng khó nhận ra các kinh nghiệm có thể chuyển đổi.",
    "Same-role candidates can still be screened out when the target stack is not visible.": "Ứng viên cùng nhóm vai trò vẫn có thể bị loại nếu CV không thể hiện rõ stack mục tiêu.",
    "Low extraction quality can make the system miss real experience.": "Chất lượng trích xuất thấp có thể khiến hệ thống bỏ sót kinh nghiệm thực tế.",
    "For a strong fit, the next improvement is usually clarity and ordering rather than adding unsupported claims.": "Khi độ phù hợp đã cao, nên ưu tiên cách diễn đạt và thứ tự nội dung thay vì thêm thông tin chưa có minh chứng.",
    "Make evidenced skills more specific": "Diễn đạt cụ thể hơn các kỹ năng đã có minh chứng",
    "Specific bullets are easier to match with JD requirements than broad claims.": "Nội dung cụ thể giúp đối chiếu với yêu cầu JD tốt hơn các mô tả chung chung.",
    "This turns a generic project line into a recruiter-readable technical responsibility.": "Cách viết này biến mô tả dự án chung chung thành trách nhiệm kỹ thuật dễ hiểu với nhà tuyển dụng."
  };
  if (exact[value]) return exact[value];

  const patterns: Array<[RegExp, (match: RegExpMatchArray) => string]> = [
    [/^Missing evidence for (.+)$/i, (m) => `Thiếu minh chứng cho kỹ năng ${m[1]}`],
    [/^JD requires (.+), but the CV does not show clear evidence for it yet\.$/i, (m) => `JD yêu cầu ${m[1]}, nhưng CV chưa thể hiện minh chứng rõ ràng cho kỹ năng này.`],
    [/^The CV has evidence for (.+), but the strongest bullet can be more explicit\.$/i, (m) => `CV đã có minh chứng cho ${m[1]}, nhưng nội dung nổi bật nhất vẫn có thể được diễn đạt cụ thể hơn.`],
    [/^The CV currently reads closer to (.+), while the JD is closer to (.+)\.$/i, (m) => `CV hiện thể hiện gần với ${formatRole(m[1])}, trong khi JD gần với ${formatRole(m[2])}.`],
    [/^Critical JD skills to prove first: (.+)\.$/i, (m) => `Các kỹ năng quan trọng trong JD cần chứng minh trước: ${m[1]}.`],
    [/^Role alignment needs attention: CV currently looks closer to (.+), while this JD looks closer to (.+)\.$/i, (m) => `Cần chú ý độ khớp vai trò: CV hiện gần với ${formatRole(m[1])}, trong khi JD gần với ${formatRole(m[2])}.`],
    [/^For a (.+) role, recruiters usually look for proof of role-critical skills, not only adjacent experience\.$/i, (m) => `Với vai trò ${formatRole(m[1])}, nhà tuyển dụng thường tìm minh chứng cho kỹ năng cốt lõi, không chỉ kinh nghiệm liên quan gián tiếp.`],
    [/^(.+) helps the CV look aligned with the target (.+) responsibilities\.$/i, (m) => `${m[1]} giúp CV thể hiện rõ hơn mức độ phù hợp với trách nhiệm ${formatRole(m[2])}.`],
    [/^If you actually used (.+), add it to a project or experience bullet with your specific responsibility\.$/i, (m) => `Nếu bạn thực sự đã dùng ${m[1]}, hãy thêm vào mô tả dự án hoặc kinh nghiệm cùng trách nhiệm cụ thể.`],
    [/^If you have real experience with (.+), add it under the most relevant project instead of only listing it in a skills section\.$/i, (m) => `Nếu có kinh nghiệm thực tế với ${m[1]}, hãy đưa minh chứng vào dự án phù hợp nhất thay vì chỉ liệt kê trong mục kỹ năng.`],
    [/^Move the most relevant (.+) project or technical responsibility higher in the CV if you have it\.$/i, (m) => `Nếu có, hãy đưa dự án hoặc trách nhiệm kỹ thuật ${formatRole(m[1])} phù hợp nhất lên vị trí dễ thấy hơn trong CV.`]
  ];
  for (const [pattern, formatter] of patterns) {
    const match = value.match(pattern);
    if (match) return formatter(match);
  }

  return value
    .replace("Rewrite generic bullets with this pattern:", "Viết lại nội dung chung chung theo cấu trúc:")
    .replace("Developed [feature] using [tech stack], responsible for [technical task], resulting in [real outcome if you can prove it].", "Phát triển [tính năng] bằng [tech stack], phụ trách [nhiệm vụ kỹ thuật], tạo ra [kết quả thực tế nếu có thể chứng minh].")
    .replace("If you have used the JD stack, add it with project evidence. If not, position your current stack as transferable and prioritize learning the missing stack.", "Nếu đã dùng stack trong JD, hãy bổ sung minh chứng từ dự án. Nếu chưa, hãy làm rõ khả năng chuyển đổi từ stack hiện tại và ưu tiên học stack còn thiếu.")
    .replace("Verify the CV preview first, then add more detailed project bullets if important content is missing.", "Hãy kiểm tra nội dung CV hệ thống đã đọc, sau đó bổ sung mô tả dự án chi tiết hơn nếu thông tin quan trọng còn thiếu.")
    .replace("Keep the most relevant project near the top and make sure each bullet shows tech stack, responsibility and real outcome.", "Đặt dự án phù hợp nhất ở vị trí dễ thấy và bảo đảm mỗi mô tả thể hiện tech stack, trách nhiệm cùng kết quả thực tế.")
    .replace("If you actually handled deployment, describe how Docker was used to run or package the backend service.", "Nếu bạn thực sự phụ trách triển khai, hãy mô tả cách Docker được dùng để chạy hoặc đóng gói dịch vụ backend.")
    .replace("Rewrite one project bullet to include the feature, tech stack, your responsibility and a real outcome if available.", "Viết lại một mô tả dự án để nêu rõ tính năng, tech stack, trách nhiệm của bạn và kết quả thực tế nếu có.");
}

function SkillList({ title, items, emptyText, tone }: { title: string; items: string[]; emptyText: string; tone: "positive" | "warning" }) {
  const textColor = tone === "positive" ? "text-emerald-200" : "text-amber-200";
  return <div className="min-w-0"><h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{title}</h4><div className="mt-3">{items.length === 0 ? <p className="text-sm text-slate-500">{emptyText}</p> : <TagList items={items} className={textColor} />}</div></div>;
}

function TagList({ items, emptyText, className = "text-slate-100" }: { items: string[]; emptyText?: string; className?: string }) {
  if (items.length === 0) return <p className="text-sm text-slate-500">{emptyText}</p>;
  return <div className="flex flex-wrap gap-2">{items.map((item, index) => <span key={`${index}-${item}`} className={`max-w-full break-words rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium ${className}`}>{item}</span>)}</div>;
}
