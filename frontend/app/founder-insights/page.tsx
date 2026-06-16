"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import { getFounderInsights, type FounderInsights } from "@/lib/api/founder-insights";
import { useAuth } from "@/lib/auth/AuthContext";

const TEXT = {
  loading: "\u0110ang t\u1ea3i founder insights...",
  title: "Founder Insights Lite",
  eyebrow: "CareerOS AI",
  description: "T\u1ed5ng h\u1ee3p t\u00edn hi\u1ec7u beta \u1edf m\u1ee9c aggregate: funnel, feedback, skill gap, matching health v\u00e0 learning loop. Kh\u00f4ng hi\u1ec3n th\u1ecb email, CV text ho\u1eb7c JD text.",
  backDashboard: "V\u1ec1 dashboard",
  refresh: "L\u00e0m m\u1edbi",
  noAccessTitle: "Kh\u00f4ng c\u00f3 quy\u1ec1n truy c\u1eadp",
  noAccessDescription: "Trang n\u00e0y ch\u1ec9 d\u00e0nh cho founder/internal user. N\u1ebfu b\u1ea1n c\u1ea7n xem, h\u00e3y c\u1eadp nh\u1eadt role t\u00e0i kho\u1ea3n \u1edf backend.",
  loadError: "Kh\u00f4ng th\u1ec3 t\u1ea3i insights. H\u00e3y ki\u1ec3m tra backend ho\u1eb7c quy\u1ec1n truy c\u1eadp.",
  funnel: "Product funnel",
  feedback: "Useful feedback",
  missingSkills: "Common missing skills",
  matchHealth: "Matching health",
  learningLoop: "Learning loop",
  empty: "Ch\u01b0a c\u00f3 d\u1eef li\u1ec7u beta cho m\u1ee5c n\u00e0y.",
  registered: "Users registered",
  profile: "Profile completed",
  cv: "Uploaded CV",
  jd: "Uploaded JD",
  analysis: "Generated analysis",
  roadmap: "Generated roadmap",
  interviewStarted: "Started interview",
  interviewCompleted: "Completed interview",
  useful: "h\u1eefu \u00edch",
  notUseful: "ch\u01b0a h\u1eefu \u00edch",
  total: "t\u1ed5ng",
  averageScore: "Average match score",
  highConfidence: "High confidence",
  mediumConfidence: "Medium confidence",
  lowConfidence: "Low confidence",
  unknownConfidence: "Unknown confidence",
  usersCompletedRoadmap: "Users completing roadmap items",
  completedItems: "Completed roadmap items",
  usersRerun: "Users rerunning analysis after roadmap"
};

export default function FounderInsightsPage() {
  const router = useRouter();
  const { user, token, isAuthenticated, isLoading } = useAuth();
  const [insights, setInsights] = useState<FounderInsights | null>(null);
  const [error, setError] = useState("");
  const [isFetching, setIsFetching] = useState(true);
  const canView = user?.role === "founder" || user?.role === "admin";

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  async function refreshInsights() {
    if (!token || !canView) {
      return;
    }
    try {
      setError("");
      setIsFetching(true);
      setInsights(await getFounderInsights(token));
    } catch (err) {
      setError(err instanceof Error ? err.message : TEXT.loadError);
    } finally {
      setIsFetching(false);
    }
  }

  useEffect(() => {
    let isMounted = true;

    async function run() {
      if (!token || !canView) {
        if (isMounted) {
          setIsFetching(false);
        }
        return;
      }
      try {
        setError("");
        setIsFetching(true);
        const data = await getFounderInsights(token);
        if (isMounted) {
          setInsights(data);
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

    void run();

    return () => {
      isMounted = false;
    };
  }, [token, canView]);

  if (isLoading || isFetching) {
    return <CenteredMessage message={TEXT.loading} />;
  }

  if (!canView) {
    return (
      <main className="min-h-screen bg-slate-950 px-4 py-10 text-white sm:px-6">
        <div className="mx-auto max-w-xl rounded-lg border border-white/10 bg-white/5 p-6 text-center">
          <h1 className="text-xl font-semibold">{TEXT.noAccessTitle}</h1>
          <p className="mt-3 text-sm leading-6 text-slate-300">{TEXT.noAccessDescription}</p>
          <Link href="/dashboard" className="mt-5 inline-flex rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-200">
            {TEXT.backDashboard}
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
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">{TEXT.eyebrow}</p>
            <h1 className="mt-1 text-xl font-semibold">{TEXT.title}</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <button type="button" onClick={() => void refreshInsights()} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              {TEXT.refresh}
            </button>
            <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              {TEXT.backDashboard}
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6">
        <p className="max-w-3xl text-sm leading-6 text-slate-300">{TEXT.description}</p>
        {error ? <p className="mt-5 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}

        {insights ? (
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <Panel title={TEXT.funnel}>
              <MetricList items={[
                [TEXT.registered, insights.funnel.registered_users],
                [TEXT.profile, insights.funnel.profile_completed_users],
                [TEXT.cv, insights.funnel.uploaded_cv_users],
                [TEXT.jd, insights.funnel.uploaded_jd_users],
                [TEXT.analysis, insights.funnel.generated_analysis_users],
                [TEXT.roadmap, insights.funnel.generated_roadmap_users],
                [TEXT.interviewStarted, insights.funnel.started_interview_users],
                [TEXT.interviewCompleted, insights.funnel.completed_interview_users]
              ]} />
            </Panel>

            <Panel title={TEXT.feedback}>
              {insights.feedback.length ? (
                <div className="space-y-3">
                  {insights.feedback.map((item) => (
                    <div key={item.feedback_type} className="rounded-md border border-white/10 bg-slate-950/60 p-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-semibold capitalize text-slate-100">{item.feedback_type}</p>
                        <p className="text-sm text-cyan-200">{item.useful_rate}% {TEXT.useful}</p>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">{item.useful} {TEXT.useful} ? {item.not_useful} {TEXT.notUseful} ? {item.total} {TEXT.total}</p>
                    </div>
                  ))}
                </div>
              ) : <Empty />}
            </Panel>

            <Panel title={TEXT.missingSkills}>
              {insights.common_missing_skills.length ? (
                <div className="flex flex-wrap gap-2">
                  {insights.common_missing_skills.map((item) => (
                    <span key={item.skill} className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-sm text-cyan-100">
                      {item.skill} ? {item.count}
                    </span>
                  ))}
                </div>
              ) : <Empty />}
            </Panel>

            <Panel title={TEXT.matchHealth}>
              <MetricList items={[
                [TEXT.averageScore, `${insights.match_health.average_match_score}%`],
                [TEXT.total, insights.match_health.total_analyses],
                [TEXT.highConfidence, insights.match_health.high_confidence_cases],
                [TEXT.mediumConfidence, insights.match_health.medium_confidence_cases],
                [TEXT.lowConfidence, insights.match_health.low_confidence_cases],
                [TEXT.unknownConfidence, insights.match_health.unknown_confidence_cases]
              ]} />
            </Panel>

            <Panel title={TEXT.learningLoop}>
              <MetricList items={[
                [TEXT.usersCompletedRoadmap, insights.learning_loop.users_completing_roadmap_items],
                [TEXT.completedItems, insights.learning_loop.completed_roadmap_items],
                [TEXT.usersRerun, insights.learning_loop.users_rerunning_analysis_after_roadmap]
              ]} />
            </Panel>
          </div>
        ) : null}
      </section>
    </main>
  );
}

function CenteredMessage({ message }: { message: string }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
      <p className="text-sm text-slate-300">{message}</p>
    </main>
  );
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
      <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function MetricList({ items }: { items: Array<[string, string | number]> }) {
  return (
    <dl className="space-y-3">
      {items.map(([label, value]) => (
        <div key={label} className="flex items-center justify-between gap-4 rounded-md border border-white/10 bg-slate-950/60 p-3">
          <dt className="break-words text-sm text-slate-300">{label}</dt>
          <dd className="shrink-0 text-sm font-semibold text-cyan-200">{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function Empty() {
  return <p className="text-sm leading-6 text-slate-400">{TEXT.empty}</p>;
}
