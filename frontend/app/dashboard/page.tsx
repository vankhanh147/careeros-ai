"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { getDashboardSummary, type DashboardSummary } from "@/lib/api/dashboard";
import { useAuth } from "@/lib/auth/AuthContext";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, logout, token } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState("");
  const [isFetching, setIsFetching] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    let isMounted = true;

    async function loadDashboard() {
      if (!token) {
        if (isMounted) {
          setIsFetching(false);
        }
        return;
      }

      try {
        setIsFetching(true);
        const data = await getDashboardSummary(token);
        if (isMounted) {
          setSummary(data);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Không thể tải dashboard.");
        }
      } finally {
        if (isMounted) {
          setIsFetching(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      isMounted = false;
    };
  }, [token]);

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  if (isLoading || isFetching) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">Đang tải dashboard...</p>
      </main>
    );
  }

  if (!summary) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="max-w-md rounded-lg border border-white/10 bg-white/5 p-6 text-center">
          <h1 className="text-xl font-semibold">Chưa tải được dashboard</h1>
          <p className="mt-2 text-sm text-slate-300">{error || "Vui lòng đăng nhập lại hoặc thử refresh trang."}</p>
          <Link href="/login" className="mt-5 inline-flex rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950">
            Về trang đăng nhập
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Dashboard tổng quan</h1>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10"
          >
            Đăng xuất
          </button>
        </div>
      </header>

      <section className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6">
        <div className="grid gap-6 lg:grid-cols-[1.35fr_0.65fr]">
          <section className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
            <p className="text-sm font-medium text-cyan-200">Career workspace</p>
            <h2 className="mt-3 break-words text-3xl font-semibold tracking-tight">Xin chào, {summary.user.full_name}</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
              Đây là trung tâm điều phối AI MVP của CareerOS AI: hồ sơ nghề nghiệp, tài liệu, matching, roadmap và mock interview trong cùng một luồng sản phẩm.
            </p>
            <dl className="mt-6 grid gap-4 sm:grid-cols-3">
              <MetricCard label="Resume" value={summary.resume_count} helper="CV đã upload" />
              <MetricCard label="Job Description" value={summary.job_description_count} helper="JD đã lưu" />
              <MetricCard label="Profile" value={summary.has_career_profile ? "Ready" : "Missing"} helper="Hồ sơ nghề nghiệp" />
            </dl>
          </section>

          <section className="min-w-0 rounded-lg border border-cyan-300/20 bg-cyan-300/10 p-5 sm:p-6">
            <h2 className="text-lg font-semibold text-cyan-50">Bước tiếp theo nên làm</h2>
            <ul className="mt-4 space-y-3">
              {summary.recommended_next_actions.map((action) => (
                <li key={action} className="rounded-md border border-cyan-300/20 bg-slate-950/40 p-3 text-sm leading-6 text-cyan-50">
                  {action}
                </li>
              ))}
            </ul>
          </section>
        </div>

        {error ? <p className="mt-6 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}

        <div className="mt-6 grid gap-6 md:grid-cols-2 xl:grid-cols-5">
          <DashboardFeatureCard
            title="Hồ sơ nghề nghiệp"
            status={summary.has_career_profile ? "Đã có dữ liệu" : "Chưa hoàn thiện"}
            description="Target role, current level, skills, experience và timeline là nền cho roadmap/interview."
            href="/profile"
            cta="Cập nhật hồ sơ"
          />
          <DashboardFeatureCard
            title="CV & JD"
            status={`${summary.resume_count} CV · ${summary.job_description_count} JD`}
            description="Quản lý CV PDF và Job Description mục tiêu để chuẩn bị cho matching."
            href="/documents"
            cta="Quản lý CV/JD"
          />
          <DashboardFeatureCard
            title="Resume ↔ JD Matching"
            status={summary.latest_analysis ? `Match ${summary.latest_analysis.match_score}%` : "Chưa có analysis"}
            description={summary.latest_analysis?.skill_gap_summary ?? "Chạy matching để nhận skill gap và improvement plan."}
            href="/analysis"
            cta="Phân tích CV ↔ JD"
          />
          <DashboardFeatureCard
            title="Roadmap"
            status={summary.latest_roadmap ? summary.latest_roadmap.timeline : "Chưa có roadmap"}
            description={summary.latest_roadmap?.title ?? "Tạo roadmap học tập ngắn hạn dựa trên skill gap và profile."}
            href="/roadmap"
            cta="Tạo roadmap"
          />
          <DashboardFeatureCard
            title="Mock Interview"
            status={summary.latest_interview ? `${summary.latest_interview.status} · ${summary.latest_interview.score ?? "--"}/100` : "Chưa luyện phỏng vấn"}
            description={summary.latest_interview ? `Gần nhất: ${summary.latest_interview.target_role}` : "Luyện phỏng vấn kỹ thuật bằng question bank rule-based."}
            href="/interview"
            cta="Luyện phỏng vấn"
          />
        </div>

        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <LatestInsightCard
            title="Latest Matching"
            empty="Chưa có kết quả matching."
            href="/analysis"
            cta="Chạy matching"
          >
            {summary.latest_analysis ? (
              <>
                <p className="text-3xl font-bold text-cyan-200">{summary.latest_analysis.match_score}%</p>
                <p className="mt-3 text-sm leading-6 text-slate-300">{summary.latest_analysis.skill_gap_summary}</p>
                <p className="mt-3 text-xs text-slate-500">{formatDate(summary.latest_analysis.created_at)}</p>
              </>
            ) : null}
          </LatestInsightCard>

          <LatestInsightCard
            title="Latest Roadmap"
            empty="Chưa có roadmap học tập."
            href="/roadmap"
            cta="Tạo roadmap"
          >
            {summary.latest_roadmap ? (
              <>
                <h3 className="break-words text-lg font-semibold text-slate-100">{summary.latest_roadmap.title}</h3>
                <p className="mt-2 text-sm text-cyan-200">Timeline: {summary.latest_roadmap.timeline}</p>
                <p className="mt-3 text-xs text-slate-500">{formatDate(summary.latest_roadmap.created_at)}</p>
              </>
            ) : null}
          </LatestInsightCard>

          <LatestInsightCard
            title="Latest Interview"
            empty="Chưa có mock interview."
            href="/interview"
            cta="Luyện phỏng vấn"
          >
            {summary.latest_interview ? (
              <>
                <h3 className="break-words text-lg font-semibold text-slate-100">{summary.latest_interview.target_role}</h3>
                <p className="mt-2 text-sm text-cyan-200">Status: {summary.latest_interview.status}</p>
                <p className="mt-2 text-sm text-slate-300">Score: {summary.latest_interview.score ?? "--"}/100</p>
                <p className="mt-3 text-xs text-slate-500">{formatDate(summary.latest_interview.created_at)}</p>
              </>
            ) : null}
          </LatestInsightCard>
        </section>
      </section>
    </main>
  );
}

function MetricCard({ label, value, helper }: { label: string; value: string | number; helper: string }) {
  return (
    <div className="min-w-0 rounded-md border border-white/10 bg-slate-950/60 p-4">
      <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</dt>
      <dd className="mt-2 break-words text-xl font-semibold text-slate-100">{value}</dd>
      <p className="mt-1 text-xs text-slate-500">{helper}</p>
    </div>
  );
}

function DashboardFeatureCard({
  title,
  status,
  description,
  href,
  cta
}: {
  title: string;
  status: string;
  description: string;
  href: string;
  cta: string;
}) {
  return (
    <article className="flex min-w-0 flex-col rounded-lg border border-white/10 bg-white/5 p-5">
      <p className="break-words text-xs font-semibold uppercase tracking-[0.16em] text-cyan-300">{status}</p>
      <h2 className="mt-3 text-lg font-semibold text-slate-100">{title}</h2>
      <p className="mt-2 flex-1 break-words text-sm leading-6 text-slate-300">{description}</p>
      <Link
        href={href}
        className="mt-5 inline-flex justify-center rounded-md bg-cyan-300 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
      >
        {cta}
      </Link>
    </article>
  );
}

function LatestInsightCard({
  title,
  empty,
  href,
  cta,
  children
}: {
  title: string;
  empty: string;
  href: string;
  cta: string;
  children: ReactNode;
}) {
  const hasContent = Boolean(children);
  return (
    <article className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
      <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
      <div className="mt-4 min-h-28">{hasContent ? children : <p className="text-sm leading-6 text-slate-400">{empty}</p>}</div>
      <Link href={href} className="mt-5 inline-flex rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
        {cta}
      </Link>
    </article>
  );
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}