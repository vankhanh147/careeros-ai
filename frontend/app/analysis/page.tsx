"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { getAnalysisHistory, runResumeJobMatch, type MatchAnalysis } from "@/lib/api/analysis";
import { getMyJobDescriptions, getMyResumes, type JobDescription, type Resume } from "@/lib/api/documents";
import { useAuth } from "@/lib/auth/AuthContext";

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
          setError(err instanceof Error ? err.message : "Không thể tải dữ liệu phân tích.");
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

  async function handleRunAnalysis(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!selectedResumeId || !selectedJobDescriptionId) {
      setError("Vui lòng chọn cả CV và Job Description để phân tích.");
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
      setStatusMessage("Đã phân tích mức độ phù hợp giữa CV và Job Description.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể chạy phân tích matching.");
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
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Resume ↔ Job Matching</h1>
          </div>
          <div className="flex gap-3">
            <Link href="/documents" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              CV và JD
            </Link>
            <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-6 py-10 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-lg border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Chọn dữ liệu phân tích</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            MVP này dùng rule-based scoring: trích xuất text từ PDF, nhận diện skill công nghệ và tính overlap với Job Description.
          </p>

          {resumes.length === 0 || jobDescriptions.length === 0 ? (
            <div className="mt-6 rounded-md border border-amber-300/20 bg-amber-300/10 p-4 text-sm leading-6 text-amber-100">
              Bạn cần có ít nhất một CV PDF và một Job Description trước khi chạy phân tích.
              <div className="mt-4">
                <Link href="/documents" className="font-semibold text-amber-50 underline underline-offset-4">
                  Thêm CV hoặc Job Description
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
                Job Description
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
                <p className="mt-2">CV: {selectedResume?.file_name ?? "Chưa chọn"}</p>
                <p className="mt-1">JD: {selectedJobDescription?.title ?? "Chưa chọn"}</p>
              </div>

              <button
                type="submit"
                disabled={isAnalyzing}
                className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isAnalyzing ? "Đang phân tích..." : "Phân tích mức độ phù hợp"}
              </button>
            </form>
          )}
        </div>

        <div className="space-y-6">
          {error ? <p className="rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
          {statusMessage ? <p className="rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}
          {currentResult ? <AnalysisResultCard analysis={currentResult} title="Kết quả vừa tạo" /> : <EmptyResult />}
        </div>
      </section>

      <section className="mx-auto w-full max-w-6xl px-6 pb-10">
        <div className="rounded-lg border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Lịch sử phân tích gần đây</h2>
          <div className="mt-4 space-y-4">
            {history.length === 0 ? (
              <p className="text-sm text-slate-400">Chưa có lịch sử phân tích.</p>
            ) : (
              history.map((analysis) => <AnalysisResultCard key={analysis.id} analysis={analysis} compact />)
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
      <h2 className="text-xl font-semibold">Kết quả matching</h2>
      <p className="mt-2 text-sm leading-6 text-slate-300">
        Chọn một CV và một JD, sau đó chạy phân tích để xem match score, kỹ năng khớp, skill gap, preview dữ liệu đã đọc và breakdown điểm.
      </p>
    </div>
  );
}

function AnalysisResultCard({ analysis, title = "Kết quả phân tích", compact = false }: { analysis: MatchAnalysis; title?: string; compact?: boolean }) {
  return (
    <article className="rounded-lg border border-white/10 bg-slate-950/60 p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
          <p className="mt-1 text-xs text-slate-500">{new Date(analysis.created_at).toLocaleString("vi-VN")}</p>
        </div>
        <div className="rounded-md bg-cyan-300 px-4 py-3 text-center text-slate-950">
          <p className="text-xs font-semibold uppercase tracking-[0.16em]">Match score</p>
          <p className="mt-1 text-2xl font-bold">{analysis.match_score}%</p>
        </div>
      </div>

      <p className="mt-4 text-sm leading-6 text-slate-300">{analysis.summary}</p>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <SkillList title="Skills đã khớp" items={analysis.matched_skills} emptyText="Chưa phát hiện skill khớp rõ ràng." tone="positive" />
        <SkillList title="Skills còn thiếu" items={analysis.missing_skills} emptyText="Chưa phát hiện skill gap lớn." tone="warning" />
      </div>

      {!compact ? (
        <>
          <div className="mt-5">
            <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Keyword overlap</h4>
            <TagList items={analysis.keyword_overlap} emptyText="Chưa có keyword overlap đáng kể." />
          </div>
          <div className="mt-5">
            <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Gợi ý cải thiện</h4>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">
              {analysis.suggestions.map((suggestion) => (
                <li key={suggestion} className="rounded-md border border-white/10 bg-white/5 p-3">{suggestion}</li>
              ))}
            </ul>
          </div>
          <DebugPreview analysis={analysis} />
        </>
      ) : null}
    </article>
  );
}

function DebugPreview({ analysis }: { analysis: MatchAnalysis }) {
  return (
    <div className="mt-6 rounded-lg border border-cyan-300/20 bg-cyan-300/5 p-5">
      <h4 className="text-base font-semibold text-cyan-100">Dữ liệu hệ thống đã đọc được</h4>
      <p className="mt-2 text-sm leading-6 text-slate-300">
        Block này giúp kiểm chứng matcher đã đọc đúng CV và JD trước khi tin vào điểm số.
      </p>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <PreviewBox title="CV text preview" text={analysis.resume_text_preview} />
        <PreviewBox title="JD text preview" text={analysis.jd_text_preview} />
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <SkillList title="Skills phát hiện trong CV" items={analysis.resume_detected_skills} emptyText="Chưa phát hiện skill trong CV." tone="positive" />
        <SkillList title="Skills phát hiện trong JD" items={analysis.jd_detected_skills} emptyText="Chưa phát hiện skill trong JD." tone="warning" />
      </div>

      <dl className="mt-5 grid gap-3 sm:grid-cols-5">
        <ScoreItem label="Skill score" value={analysis.scoring_breakdown.skill_score} />
        <ScoreItem label="Keyword score" value={analysis.scoring_breakdown.keyword_score} />
        <ScoreItem label="Semantic score" value={analysis.scoring_breakdown.semantic_score} />
        <ScoreItem label="Length sanity" value={analysis.scoring_breakdown.length_sanity} />
        <ScoreItem label="Final score" value={analysis.scoring_breakdown.final_score} />
      </dl>
    </div>
  );
}

function PreviewBox({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <h5 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{title}</h5>
      <p className="mt-3 max-h-48 overflow-auto rounded-md border border-white/10 bg-slate-950/80 p-3 text-sm leading-6 text-slate-300">
        {text || "Không có text preview."}
      </p>
    </div>
  );
}

function ScoreItem({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-white/10 bg-slate-950/70 p-3">
      <dt className="text-xs uppercase tracking-[0.16em] text-slate-500">{label}</dt>
      <dd className="mt-2 text-lg font-semibold text-slate-100">{value}</dd>
    </div>
  );
}

function SkillList({ title, items, emptyText, tone }: { title: string; items: string[]; emptyText: string; tone: "positive" | "warning" }) {
  const textColor = tone === "positive" ? "text-emerald-200" : "text-amber-200";
  return (
    <div>
      <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{title}</h4>
      <div className="mt-3">
        {items.length === 0 ? <p className="text-sm text-slate-500">{emptyText}</p> : <TagList items={items} className={textColor} />}
      </div>
    </div>
  );
}

function TagList({ items, emptyText, className = "text-slate-100" }: { items: string[]; emptyText?: string; className?: string }) {
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">{emptyText}</p>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span key={item} className={`rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium ${className}`}>
          {item}
        </span>
      ))}
    </div>
  );
}