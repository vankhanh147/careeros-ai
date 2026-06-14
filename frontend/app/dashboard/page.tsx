
"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { getDashboardSummary, type DashboardSummary } from "@/lib/api/dashboard";
import { useAuth } from "@/lib/auth/AuthContext";

type NextAction = {
  title: string;
  description: string;
  href: string;
  cta: string;
  tone: "primary" | "secondary";
};

const TEXT = {
  loadingTitle: "\u0110ang t\u1ea3i dashboard...",
  loadingDescription: "CareerOS AI \u0111ang \u0111\u1ed3ng b\u1ed9 tr\u1ea1ng th\u00e1i h\u1ed3 s\u01a1, CV/JD v\u00e0 c\u00e1c k\u1ebft qu\u1ea3 AI g\u1ea7n nh\u1ea5t.",
  loadError: "Kh\u00f4ng th\u1ec3 t\u1ea3i dashboard. Vui l\u00f2ng ki\u1ec3m tra backend v\u00e0 th\u1eed l\u1ea1i.",
  loadFailedTitle: "Ch\u01b0a t\u1ea3i \u0111\u01b0\u1ee3c dashboard",
  loginAgain: "Vui l\u00f2ng \u0111\u0103ng nh\u1eadp l\u1ea1i ho\u1eb7c ki\u1ec3m tra backend \u0111ang ch\u1ea1y.",
  retry: "Th\u1eed t\u1ea3i l\u1ea1i",
  backToLogin: "V\u1ec1 trang \u0111\u0103ng nh\u1eadp",
  dashboardTitle: "Dashboard t\u1ed5ng quan",
  refresh: "L\u00e0m m\u1edbi",
  logout: "\u0110\u0103ng xu\u1ea5t",
  careerWorkspace: "Kh\u00f4ng gian ngh\u1ec1 nghi\u1ec7p",
  hello: "Xin ch\u00e0o",
  heroDescription: "\u0110\u00e2y l\u00e0 trung t\u00e2m \u0111i\u1ec1u ph\u1ed1i CareerOS AI: h\u1ed3 s\u01a1 ngh\u1ec1 nghi\u1ec7p, CV/JD, Resume \u2194 JD Matching, Roadmap v\u00e0 Mock Interview trong c\u00f9ng m\u1ed9t workflow beta.",
  progressLabel: "M\u1ee9c ho\u00e0n thi\u1ec7n MVP flow",
  uploadedCv: "CV \u0111\u00e3 upload",
  savedJd: "Job Description \u0111\u00e3 l\u01b0u",
  profileLabel: "H\u1ed3 s\u01a1",
  profileAvailable: "\u0110\u00e3 c\u00f3",
  profileMissing: "Ch\u01b0a c\u00f3",
  careerProfile: "H\u1ed3 s\u01a1 ngh\u1ec1 nghi\u1ec7p",
  nextStepTitle: "B\u01b0\u1edbc ti\u1ebfp theo n\u00ean l\u00e0m",
  nextStepDescription: "CareerOS AI \u01b0u ti\u00ean h\u00e0nh \u0111\u1ed9ng c\u00f3 t\u00e1c \u0111\u1ed9ng nh\u1ea5t d\u1ef1a tr\u00ean d\u1eef li\u1ec7u hi\u1ec7n t\u1ea1i c\u1ee7a b\u1ea1n.",
  profileReady: "\u0110\u00e3 c\u00f3 d\u1eef li\u1ec7u",
  profileIncomplete: "Ch\u01b0a ho\u00e0n thi\u1ec7n",
  updateProfile: "C\u1eadp nh\u1eadt h\u1ed3 s\u01a1",
  profileCardDescription: "Target role, current level, k\u1ef9 n\u0103ng, kinh nghi\u1ec7m v\u00e0 timeline l\u00e0 n\u1ec1n d\u1eef li\u1ec7u cho roadmap/interview.",
  manageCvJd: "Qu\u1ea3n l\u00fd CV/JD",
  cvJdCardDescription: "Qu\u1ea3n l\u00fd CV PDF v\u00e0 Job Description m\u1ee5c ti\u00eau \u0111\u1ec3 chu\u1ea9n b\u1ecb cho matching.",
  matchScore: "\u0110i\u1ec3m ph\u00f9 h\u1ee3p",
  noAnalysis: "Ch\u01b0a c\u00f3 ph\u00e2n t\u00edch",
  analysisCardDescription: "Ch\u1ea1y matching \u0111\u1ec3 nh\u1eadn skill gap v\u00e0 improvement plan.",
  analyzeCvJd: "Ph\u00e2n t\u00edch CV \u2194 JD",
  noRoadmap: "Ch\u01b0a c\u00f3 roadmap",
  roadmapCardDescription: "T\u1ea1o roadmap h\u1ecdc t\u1eadp ng\u1eafn h\u1ea1n d\u1ef1a tr\u00ean skill gap v\u00e0 profile.",
  createRoadmap: "T\u1ea1o roadmap",
  noInterview: "Ch\u01b0a luy\u1ec7n ph\u1ecfng v\u1ea5n",
  interviewCardDescription: "Luy\u1ec7n ph\u1ecfng v\u1ea5n k\u1ef9 thu\u1eadt b\u1eb1ng question bank rule-based.",
  latest: "G\u1ea7n nh\u1ea5t",
  practiceInterview: "Luy\u1ec7n ph\u1ecfng v\u1ea5n",
  latestAnalysis: "Ph\u00e2n t\u00edch g\u1ea7n nh\u1ea5t",
  latestAnalysisEmpty: "Ch\u01b0a c\u00f3 k\u1ebft qu\u1ea3 matching. H\u00e3y ch\u1ecdn CV v\u00e0 JD \u0111\u1ec3 ch\u1ea1y ph\u00e2n t\u00edch \u0111\u1ea7u ti\u00ean.",
  runMatching: "Ch\u1ea1y matching",
  latestRoadmap: "Roadmap g\u1ea7n nh\u1ea5t",
  latestRoadmapEmpty: "Ch\u01b0a c\u00f3 roadmap h\u1ecdc t\u1eadp. T\u1ea1o roadmap sau khi c\u00f3 profile ho\u1eb7c analysis.",
  timeline: "Timeline",
  latestInterview: "Phi\u00ean ph\u1ecfng v\u1ea5n g\u1ea7n nh\u1ea5t",
  latestInterviewEmpty: "Ch\u01b0a c\u00f3 Mock Interview. B\u1eaft \u0111\u1ea7u m\u1ed9t phi\u00ean luy\u1ec7n t\u1eadp khi b\u1ea1n \u0111\u00e3 c\u00f3 target role.",
  status: "Tr\u1ea1ng th\u00e1i",
  score: "\u0110i\u1ec3m",
  inProgress: "\u0110ang luy\u1ec7n",
  finished: "Ho\u00e0n t\u1ea5t",
  none: "Ch\u01b0a c\u00f3",
  unfinished: "Ch\u01b0a ho\u00e0n th\u00e0nh"
};

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

  const loadDashboard = useCallback(async () => {
    if (!token) {
      setIsFetching(false);
      return;
    }

    try {
      setError("");
      setIsFetching(true);
      const data = await getDashboardSummary(token);
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : TEXT.loadError);
    } finally {
      setIsFetching(false);
    }
  }, [token]);

  useEffect(() => {
    let isMounted = true;

    async function run() {
      if (!isMounted) return;
      await loadDashboard();
    }

    void run();

    return () => {
      isMounted = false;
    };
  }, [loadDashboard]);

  const nextActions = useMemo(() => (summary ? buildNextActions(summary) : []), [summary]);
  const progress = useMemo(() => (summary ? getProgress(summary) : { completed: 0, total: 5, percent: 0 }), [summary]);

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  if (isLoading || isFetching) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="rounded-lg border border-white/10 bg-white/5 p-6 text-center">
          <p className="text-sm font-medium text-slate-100">{TEXT.loadingTitle}</p>
          <p className="mt-2 text-xs text-slate-500">{TEXT.loadingDescription}</p>
        </div>
      </main>
    );
  }

  if (!summary) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="max-w-md rounded-lg border border-white/10 bg-white/5 p-6 text-center">
          <h1 className="text-xl font-semibold">{TEXT.loadFailedTitle}</h1>
          <p className="mt-2 text-sm leading-6 text-slate-300">{error || TEXT.loginAgain}</p>
          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <button type="button" onClick={() => void loadDashboard()} className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200">
              {TEXT.retry}
            </button>
            <Link href="/login" className="rounded-md border border-white/15 px-5 py-3 text-sm font-semibold transition hover:bg-white/10">
              {TEXT.backToLogin}
            </Link>
          </div>
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
            <h1 className="mt-1 text-xl font-semibold">{TEXT.dashboardTitle}</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <button type="button" onClick={() => void loadDashboard()} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              {TEXT.refresh}
            </button>
            <button type="button" onClick={handleLogout} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              {TEXT.logout}
            </button>
          </div>
        </div>
      </header>

      <section className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6">
        <div className="grid gap-6 lg:grid-cols-[1.35fr_0.65fr]">
          <section className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
            <p className="text-sm font-medium text-cyan-200">{TEXT.careerWorkspace}</p>
            <h2 className="mt-3 break-words text-3xl font-semibold tracking-tight">{TEXT.hello}, {summary.user.full_name}</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">{TEXT.heroDescription}</p>
            <div className="mt-6 rounded-md border border-white/10 bg-slate-950/60 p-4">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-slate-100">{TEXT.progressLabel}</span>
                <span className="text-cyan-200">{progress.completed}/{progress.total}</span>
              </div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                <div className="h-full rounded-full bg-cyan-300 transition-all" style={{ width: `${progress.percent}%` }} />
              </div>
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-3">
              <MetricCard label="CV" value={summary.resume_count} helper={TEXT.uploadedCv} />
              <MetricCard label="JD" value={summary.job_description_count} helper={TEXT.savedJd} />
              <MetricCard label={TEXT.profileLabel} value={summary.has_career_profile ? TEXT.profileAvailable : TEXT.profileMissing} helper={TEXT.careerProfile} />
            </dl>
          </section>

          <section className="min-w-0 rounded-lg border border-cyan-300/20 bg-cyan-300/10 p-5 sm:p-6">
            <h2 className="text-lg font-semibold text-cyan-50">{TEXT.nextStepTitle}</h2>
            <p className="mt-2 text-sm leading-6 text-cyan-100/80">{TEXT.nextStepDescription}</p>
            <ul className="mt-4 space-y-3">
              {nextActions.map((action) => (
                <li key={action.title} className="rounded-md border border-cyan-300/20 bg-slate-950/40 p-3 text-sm leading-6 text-cyan-50">
                  <div className="flex flex-col gap-3">
                    <div className="min-w-0">
                      <p className="break-words font-semibold">{action.title}</p>
                      <p className="mt-1 break-words text-xs leading-5 text-cyan-100/75">{action.description}</p>
                    </div>
                    <Link href={action.href} className={`${action.tone === "primary" ? "bg-cyan-300 text-slate-950 hover:bg-cyan-200" : "border border-cyan-300/30 text-cyan-50 hover:bg-cyan-300/10"} rounded-md px-3 py-2 text-center text-xs font-semibold transition`}>
                      {action.cta}
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        </div>

        {error ? <p className="mt-6 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}

        <div className="mt-6 grid gap-6 md:grid-cols-2 xl:grid-cols-5">
          <DashboardFeatureCard title={TEXT.careerProfile} status={summary.has_career_profile ? TEXT.profileReady : TEXT.profileIncomplete} description={TEXT.profileCardDescription} href="/profile" cta={TEXT.updateProfile} />
          <DashboardFeatureCard title="CV & JD" status={`${summary.resume_count} CV ? ${summary.job_description_count} JD`} description={TEXT.cvJdCardDescription} href="/documents" cta={TEXT.manageCvJd} />
          <DashboardFeatureCard title="Resume ? JD Matching" status={summary.latest_analysis ? `${TEXT.matchScore} ${summary.latest_analysis.match_score}%` : TEXT.noAnalysis} description={summary.latest_analysis?.skill_gap_summary ?? TEXT.analysisCardDescription} href="/analysis" cta={TEXT.analyzeCvJd} />
          <DashboardFeatureCard title="Roadmap" status={summary.latest_roadmap ? summary.latest_roadmap.timeline : TEXT.noRoadmap} description={summary.latest_roadmap?.title ?? TEXT.roadmapCardDescription} href="/roadmap" cta={TEXT.createRoadmap} />
          <DashboardFeatureCard title="Mock Interview" status={summary.latest_interview ? `${formatInterviewStatus(summary.latest_interview.status)} ? ${formatInterviewScore(summary.latest_interview.score)}` : TEXT.noInterview} description={summary.latest_interview ? `${TEXT.latest}: ${summary.latest_interview.target_role}` : TEXT.interviewCardDescription} href="/interview" cta={TEXT.practiceInterview} />
        </div>

        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <LatestInsightCard title={TEXT.latestAnalysis} empty={TEXT.latestAnalysisEmpty} href="/analysis" cta={TEXT.runMatching}>
            {summary.latest_analysis ? (
              <>
                <p className="text-3xl font-bold text-cyan-200">{summary.latest_analysis.match_score}%</p>
                <p className="mt-3 break-words text-sm leading-6 text-slate-300">{summary.latest_analysis.skill_gap_summary}</p>
                <p className="mt-3 text-xs text-slate-500">{formatDate(summary.latest_analysis.created_at)}</p>
              </>
            ) : null}
          </LatestInsightCard>

          <LatestInsightCard title={TEXT.latestRoadmap} empty={TEXT.latestRoadmapEmpty} href="/roadmap" cta={TEXT.createRoadmap}>
            {summary.latest_roadmap ? (
              <>
                <h3 className="break-words text-lg font-semibold text-slate-100">{summary.latest_roadmap.title}</h3>
                <p className="mt-2 text-sm text-cyan-200">{TEXT.timeline}: {summary.latest_roadmap.timeline}</p>
                <p className="mt-3 text-xs text-slate-500">{formatDate(summary.latest_roadmap.created_at)}</p>
              </>
            ) : null}
          </LatestInsightCard>

          <LatestInsightCard title={TEXT.latestInterview} empty={TEXT.latestInterviewEmpty} href="/interview" cta={TEXT.practiceInterview}>
            {summary.latest_interview ? (
              <>
                <h3 className="break-words text-lg font-semibold text-slate-100">{summary.latest_interview.target_role}</h3>
                <p className="mt-2 text-sm text-cyan-200">{TEXT.status}: {formatInterviewStatus(summary.latest_interview.status)}</p>
                <p className="mt-2 text-sm text-slate-300">{TEXT.score}: {formatInterviewScore(summary.latest_interview.score)}</p>
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

function DashboardFeatureCard({ title, status, description, href, cta }: { title: string; status: string; description: string; href: string; cta: string }) {
  return (
    <article className="flex min-w-0 flex-col rounded-lg border border-white/10 bg-white/5 p-5">
      <p className="break-words text-xs font-semibold uppercase tracking-[0.16em] text-cyan-300">{status}</p>
      <h2 className="mt-3 text-lg font-semibold text-slate-100">{title}</h2>
      <p className="mt-2 flex-1 break-words text-sm leading-6 text-slate-300">{description}</p>
      <Link href={href} className="mt-5 inline-flex justify-center rounded-md bg-cyan-300 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200">
        {cta}
      </Link>
    </article>
  );
}

function LatestInsightCard({ title, empty, href, cta, children }: { title: string; empty: string; href: string; cta: string; children: ReactNode }) {
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

function buildNextActions(summary: DashboardSummary): NextAction[] {
  if (!summary.has_career_profile) {
    return [
      { title: "Ho\u00e0n thi\u1ec7n h\u1ed3 s\u01a1 ngh\u1ec1 nghi\u1ec7p", description: "Nh\u1eadp target role, k\u1ef9 n\u0103ng v\u00e0 timeline \u0111\u1ec3 c\u00e1c module AI c\u00f3 ng\u1eef c\u1ea3nh t\u1ed1t h\u01a1n.", href: "/profile", cta: TEXT.updateProfile, tone: "primary" },
      { title: "Chu\u1ea9n b\u1ecb CV v\u00e0 JD", description: "B\u1ea1n v\u1eabn c\u00f3 th\u1ec3 upload CV/JD tr\u01b0\u1edbc khi profile ho\u00e0n ch\u1ec9nh.", href: "/documents", cta: TEXT.manageCvJd, tone: "secondary" }
    ];
  }
  if (summary.resume_count === 0 || summary.job_description_count === 0) {
    return [
      { title: "Upload CV v\u00e0 th\u00eam JD m\u1ee5c ti\u00eau", description: "C\u1ea7n \u00edt nh\u1ea5t m\u1ed9t CV v\u00e0 m\u1ed9t JD \u0111\u1ec3 ch\u1ea1y Resume \u2194 JD Matching.", href: "/documents", cta: "Th\u00eam CV/JD", tone: "primary" },
      { title: "Ki\u1ec3m tra l\u1ea1i profile", description: "Profile t\u1ed1t gi\u00fap roadmap v\u00e0 ph\u1ecfng v\u1ea5n s\u00e1t m\u1ee5c ti\u00eau h\u01a1n.", href: "/profile", cta: "Xem profile", tone: "secondary" }
    ];
  }
  if (!summary.latest_analysis) {
    return [
      { title: "Ch\u1ea1y Resume \u2194 JD Matching", description: "Ph\u00e2n t\u00edch m\u1ee9c ph\u00f9 h\u1ee3p, skill gap v\u00e0 c\u00e1c g\u1ee3i \u00fd c\u1ea3i thi\u1ec7n CV.", href: "/analysis", cta: TEXT.runMatching, tone: "primary" },
      { title: "Qu\u1ea3n l\u00fd th\u00eam JD kh\u00e1c", description: "Th\u1eed nhi\u1ec1u JD gi\u00fap b\u1ea1n hi\u1ec3u th\u1ecb tr\u01b0\u1eddng v\u00e0 ch\u1ecdn m\u1ee5c ti\u00eau ph\u00f9 h\u1ee3p h\u01a1n.", href: "/documents", cta: "Th\u00eam JD", tone: "secondary" }
    ];
  }
  if (!summary.latest_roadmap) {
    return [
      { title: "T\u1ea1o roadmap h\u1ecdc t\u1eadp", description: "Bi\u1ebfn skill gap th\u00e0nh k\u1ebf ho\u1ea1ch h\u00e0nh \u0111\u1ed9ng ng\u1eafn h\u1ea1n, d\u1ec5 b\u1eaft \u0111\u1ea7u.", href: "/roadmap", cta: TEXT.createRoadmap, tone: "primary" },
      { title: "Xem l\u1ea1i ph\u00e2n t\u00edch g\u1ea7n nh\u1ea5t", description: "Ki\u1ec3m tra preview CV/JD v\u00e0 breakdown \u0111\u1ec3 ch\u1eafc h\u1ec7 th\u1ed1ng \u0111\u1ecdc \u0111\u00fang d\u1eef li\u1ec7u.", href: "/analysis", cta: "Xem analysis", tone: "secondary" }
    ];
  }
  if (!summary.latest_interview || summary.latest_interview.status !== "finished") {
    return [
      { title: "Luy\u1ec7n Mock Interview", description: "D\u00f9ng target role v\u00e0 skill gap \u0111\u1ec3 luy\u1ec7n c\u00e1c c\u00e2u h\u1ecfi k\u1ef9 thu\u1eadt \u0111\u1ea7u ti\u00ean.", href: "/interview", cta: TEXT.practiceInterview, tone: "primary" },
      { title: "Theo roadmap", description: "D\u00e0nh th\u1eddi gian ho\u00e0n th\u00e0nh output c\u1ee7a t\u1eebng b\u01b0\u1edbc tr\u01b0\u1edbc khi apply.", href: "/roadmap", cta: "Xem roadmap", tone: "secondary" }
    ];
  }
  return [
    { title: "Th\u1eed JD m\u1edbi ho\u1eb7c c\u1ea3i thi\u1ec7n CV", description: "B\u1ea1n \u0111\u00e3 \u0111i h\u1ebft MVP flow. H\u00e3y d\u00f9ng feedback \u0111\u1ec3 t\u1ed1i \u01b0u CV ho\u1eb7c th\u1eed m\u1ed9t JD kh\u00f3 h\u01a1n.", href: "/documents", cta: "Th\u00eam JD m\u1edbi", tone: "primary" },
    { title: "Ch\u1ea1y l\u1ea1i matching", description: "Sau khi s\u1eeda CV, ch\u1ea1y l\u1ea1i analysis \u0111\u1ec3 xem score v\u00e0 skill gap thay \u0111\u1ed5i th\u1ebf n\u00e0o.", href: "/analysis", cta: "Ph\u00e2n t\u00edch l\u1ea1i", tone: "secondary" }
  ];
}

function getProgress(summary: DashboardSummary) {
  const checks = [
    summary.has_career_profile,
    summary.resume_count > 0 && summary.job_description_count > 0,
    Boolean(summary.latest_analysis),
    Boolean(summary.latest_roadmap),
    Boolean(summary.latest_interview?.status === "finished")
  ];
  const completed = checks.filter(Boolean).length;
  return { completed, total: checks.length, percent: Math.round((completed / checks.length) * 100) };
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}

function formatInterviewStatus(status: string) {
  if (status === "in_progress") return TEXT.inProgress;
  if (status === "finished") return TEXT.finished;
  return status || TEXT.none;
}

function formatInterviewScore(score: number | null) {
  return score === null ? TEXT.unfinished : `${score}/100`;
}
