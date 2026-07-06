"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { getDashboardSummary, type DashboardSummary } from "@/lib/api/dashboard";
import { useAuth } from "@/lib/auth/AuthContext";
import { StatusBadge } from "@/components/ui/ProductUI";

type WorkspaceAction = {
  title: string;
  description: string;
  href: string;
  cta: string;
};

type HealthCheck = {
  label: string;
  complete: boolean;
};

type RecentActivity = {
  title: string;
  detail: string;
  createdAt: string;
  href: string;
  marker: string;
};

const QUICK_ACTIONS = [
  { href: "/profile", label: "Hồ sơ nghề nghiệp", marker: "HS" },
  { href: "/documents", label: "CV & JD", marker: "CV" },
  { href: "/analysis", label: "Resume ↔ JD Matching", marker: "M" },
  { href: "/roadmap", label: "Roadmap học tập", marker: "R" },
  { href: "/interview", label: "Mock Interview", marker: "MI" }
];

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
      setSummary(await getDashboardSummary(token));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tải Dashboard. Vui lòng kiểm tra kết nối backend.");
    } finally {
      setIsFetching(false);
    }
  }, [token]);

  useEffect(() => {
    let isMounted = true;

    async function run() {
      if (isMounted) {
        await loadDashboard();
      }
    }

    void run();
    return () => {
      isMounted = false;
    };
  }, [loadDashboard]);

  const health = useMemo(() => summary ? buildCareerHealth(summary) : null, [summary]);
  const nextAction = useMemo(() => summary ? buildNextAction(summary) : null, [summary]);
  const activities = useMemo(() => summary ? buildRecentActivities(summary) : [], [summary]);

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  if (isLoading || isFetching) {
    return <DashboardSkeleton />;
  }

  if (!summary || !health || !nextAction) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <section className="w-full max-w-md rounded-lg border border-white/10 bg-white/5 p-6 text-center">
          <h1 className="text-xl font-semibold">Chưa tải được Career Workspace</h1>
          <p className="mt-2 text-sm leading-6 text-slate-300">{error || "Vui lòng đăng nhập lại hoặc kiểm tra backend đang chạy."}</p>
          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <button type="button" onClick={() => void loadDashboard()} className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
              Thử tải lại
            </button>
            <Link href="/login" className="rounded-md border border-white/15 px-5 py-3 text-sm font-semibold transition hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
              Về trang đăng nhập
            </Link>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Career Workspace</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <button type="button" onClick={() => void loadDashboard()} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
              Làm mới
            </button>
            <button type="button" onClick={handleLogout} className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      <section className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        <div className="max-w-3xl">
          <p className="text-sm font-medium text-cyan-200">Không gian nghề nghiệp</p>
          <h2 className="mt-2 break-words text-2xl font-semibold sm:text-3xl">Xin chào, {summary.user.full_name}</h2>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Theo dõi mức độ sẵn sàng của hồ sơ, Matching, Roadmap và Mock Interview trong một luồng thống nhất.
          </p>
        </div>

        {error ? <p className="mt-5 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}

        <div className="mt-7 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
          <CareerHealthCard health={health} nextAction={nextAction} />
          <NextActionCard action={nextAction} summary={summary} />
        </div>

        <section className="mt-8">
          <div>
            <p className="text-sm font-medium text-cyan-200">Trạng thái hiện tại</p>
            <h2 className="mt-1 text-xl font-semibold">Career Workspace</h2>
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <WorkspaceCard title="Hồ sơ nghề nghiệp" status={summary.has_career_profile ? "Đã sẵn sàng" : "Chưa hoàn thiện"} description={summary.has_career_profile ? "Đã có dữ liệu nền cho các gợi ý cá nhân hóa." : "Cần bổ sung vai trò, kỹ năng và mục tiêu nghề nghiệp."} href="/profile" cta="Cập nhật hồ sơ" ready={summary.has_career_profile} />
            <WorkspaceCard title="CV" status={summary.resume_count > 0 ? `${summary.resume_count} CV đã lưu` : "Chưa có CV"} description={summary.resume_count > 0 ? "CV đã sẵn sàng để chọn khi chạy Matching." : "Tải CV PDF lên để bắt đầu phân tích."} href="/documents" cta="Quản lý CV" ready={summary.resume_count > 0} />
            <WorkspaceCard title="Job Description" status={summary.job_description_count > 0 ? `${summary.job_description_count} JD đã lưu` : "Chưa có JD"} description={summary.job_description_count > 0 ? "JD mục tiêu đã sẵn sàng để so khớp." : "Thêm một JD phù hợp với vai trò mục tiêu."} href="/documents" cta="Quản lý JD" ready={summary.job_description_count > 0} />
            <WorkspaceCard title="Resume ↔ JD Matching" status={summary.latest_analysis ? `${summary.latest_analysis.match_score}% phù hợp` : "Chưa có Matching"} description={summary.latest_analysis?.skill_gap_summary ?? "Chạy phân tích để thấy kỹ năng đã khớp và khoảng trống cần cải thiện."} href="/analysis" cta="Mở Matching" ready={Boolean(summary.latest_analysis)} />
            <WorkspaceCard title="Roadmap" status={summary.latest_roadmap ? `${summary.latest_roadmap.completed_items}/${summary.latest_roadmap.total_items} bước hoàn thành` : "Chưa có Roadmap"} description={summary.latest_roadmap?.title ?? "Chuyển skill gap thành kế hoạch học tập và minh chứng CV."} href="/roadmap" cta="Mở Roadmap" ready={Boolean(summary.latest_roadmap)} />
            <WorkspaceCard title="Mock Interview" status={summary.latest_interview ? `${formatInterviewStatus(summary.latest_interview.status)} · ${formatInterviewScore(summary.latest_interview.score)}` : "Chưa luyện"} description={summary.latest_interview ? `Vai trò gần nhất: ${summary.latest_interview.target_role}` : "Luyện câu hỏi kỹ thuật theo vai trò và điểm cần cải thiện."} href="/interview" cta="Mở Mock Interview" ready={Boolean(summary.latest_interview)} />
          </div>
        </section>

        <div className="mt-8 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
          <RecentActivitySection activities={activities} />
          <QuickActions />
        </div>
      </section>
    </main>
  );
}

function DashboardSkeleton() {
  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6">
      <div className="mx-auto w-full max-w-6xl animate-pulse">
        <div className="h-6 w-40 rounded bg-white/10" />
        <div className="mt-5 h-9 max-w-md rounded bg-white/10" />
        <div className="mt-8 grid gap-5 lg:grid-cols-2">
          <div className="h-72 rounded-lg border border-white/10 bg-white/5" />
          <div className="h-72 rounded-lg border border-white/10 bg-white/5" />
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => <div key={index} className="h-44 rounded-lg border border-white/10 bg-white/5" />)}
        </div>
        <p className="sr-only">Đang tải Career Workspace...</p>
      </div>
    </main>
  );
}

function CareerHealthCard({ health, nextAction }: { health: ReturnType<typeof buildCareerHealth>; nextAction: WorkspaceAction }) {
  return (
    <section className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium text-cyan-200">Career Health</p>
          <h2 className="mt-1 text-xl font-semibold">Mức độ hoàn thiện hành trình</h2>
        </div>
        <div className="flex items-baseline gap-2 sm:text-right">
          <p className="text-4xl font-bold text-cyan-200">{health.percent}%</p>
          <span className="text-xs font-medium text-slate-500">đã hoàn thiện</span>
        </div>
      </div>
      <div
        className="mt-4 h-3 overflow-hidden rounded-full bg-white/10"
        role="progressbar"
        aria-label="Mức độ hoàn thiện Career Health"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={health.percent}
      >
        <div className="h-full rounded-full bg-cyan-300 transition-[width]" style={{ width: `${health.percent}%` }} />
      </div>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <HealthList title="Đã hoàn thành" items={health.completed} tone="positive" />
        <HealthList title="Còn thiếu" items={health.missing} tone="muted" />
      </div>
      <div className="mt-5 rounded-md border border-cyan-300/20 bg-cyan-300/5 p-3 text-sm">
        <span className="font-semibold text-cyan-100">Tiếp theo nên làm:</span>
        <span className="ml-2 text-slate-300">{nextAction.title}</span>
      </div>
    </section>
  );
}

function HealthList({ title, items, tone }: { title: string; items: string[]; tone: "positive" | "muted" }) {
  return (
    <div className="min-w-0">
      <h3 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">{title}</h3>
      {items.length > 0 ? (
        <ul className="mt-2 space-y-2 text-sm">
          {items.map((item) => <li key={`${title}-${item}`} className={tone === "positive" ? "text-emerald-200" : "text-slate-400"}>{tone === "positive" ? "✓" : "•"} {item}</li>)}
        </ul>
      ) : <p className="mt-2 text-sm text-slate-500">{tone === "positive" ? "Chưa có bước hoàn thành." : "Không còn bước bắt buộc."}</p>}
    </div>
  );
}

function NextActionCard({ action, summary }: { action: WorkspaceAction; summary: DashboardSummary }) {
  const context = buildNextActionContext(summary, action);
  return (
    <section className="flex min-w-0 flex-col rounded-lg border border-cyan-300/20 bg-cyan-300/10 p-5 sm:p-6">
      <p className="text-sm font-medium text-cyan-100">Việc tiếp theo</p>
      <h2 className="mt-2 break-words text-xl font-semibold text-cyan-50">{action.title}</h2>
      <p className="mt-3 break-words text-sm leading-6 text-cyan-100/80">{action.description}</p>
      <div className="mt-5 rounded-md border border-cyan-100/15 bg-slate-950/20 p-3">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-cyan-100/60">Dữ liệu hiện tại</p>
        <p className="mt-1 break-words text-sm text-cyan-50">{context}</p>
      </div>
      <Link href={action.href} className="mt-5 inline-flex justify-center rounded-md bg-cyan-300 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
        {action.cta}
      </Link>
    </section>
  );
}

function WorkspaceCard({ title, status, description, href, cta, ready }: { title: string; status: string; description: string; href: string; cta: string; ready: boolean }) {
  return (
    <article className="flex min-w-0 flex-col rounded-lg border border-white/10 bg-white/5 p-5">
      <StatusBadge tone={ready ? "success" : "neutral"}>{status}</StatusBadge>
      <h3 className="mt-4 text-lg font-semibold text-slate-100">{title}</h3>
      <p className="mt-2 line-clamp-3 min-h-18 flex-1 break-words text-sm leading-6 text-slate-300">{description}</p>
      <Link href={href} className="mt-5 inline-flex justify-center rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
        {cta}
      </Link>
    </article>
  );
}

function RecentActivitySection({ activities }: { activities: RecentActivity[] }) {
  return (
    <section className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
      <h2 className="text-lg font-semibold">Hoạt động gần đây</h2>
      {activities.length > 0 ? (
        <ol className="mt-4 space-y-3">
          {activities.map((activity) => (
            <li key={`${activity.title}-${activity.createdAt}`} className="rounded-md border border-white/10 bg-slate-950/50 p-3">
              <div className="flex min-w-0 flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="flex items-start gap-3">
                    <span aria-hidden="true" className="flex h-7 min-w-7 items-center justify-center rounded-md border border-cyan-300/20 bg-cyan-300/10 px-1 text-[10px] font-bold text-cyan-200">{activity.marker}</span>
                    <p className="break-words pt-1 text-sm font-semibold text-slate-100">{activity.title}</p>
                  </div>
                  <p className="mt-1 break-words text-xs text-slate-400">{activity.detail}</p>
                </div>
                <time className="shrink-0 text-xs text-slate-500">{formatDate(activity.createdAt)}</time>
              </div>
              <Link href={activity.href} className="mt-2 inline-flex text-xs font-semibold text-cyan-200 hover:text-cyan-100">Xem chi tiết</Link>
            </li>
          ))}
        </ol>
      ) : <p className="mt-3 text-sm leading-6 text-slate-400">Chưa có hoạt động để hiển thị. Hãy hoàn thiện hồ sơ hoặc thêm CV/JD để bắt đầu.</p>}
    </section>
  );
}

function QuickActions() {
  return (
    <nav aria-label="Thao tác nhanh" className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
      <h2 className="text-lg font-semibold">Thao tác nhanh</h2>
      <div className="mt-4 grid gap-3">
        {QUICK_ACTIONS.map((action) => (
          <Link key={action.href} href={action.href} className="flex items-center justify-between gap-3 rounded-md border border-white/10 bg-slate-950/40 px-4 py-3 text-sm font-semibold transition hover:border-cyan-300/30 hover:bg-cyan-300/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
            <span className="break-words">{action.label}</span>
            <span aria-hidden="true" className="flex h-7 min-w-7 items-center justify-center rounded-md border border-cyan-300/20 bg-cyan-300/10 px-1 text-[10px] font-bold text-cyan-200">{action.marker}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
}

function buildCareerHealth(summary: DashboardSummary) {
  const checks: HealthCheck[] = [
    { label: "Hồ sơ nghề nghiệp", complete: summary.has_career_profile },
    { label: "CV", complete: summary.resume_count > 0 },
    { label: "Job Description", complete: summary.job_description_count > 0 },
    { label: "Resume ↔ JD Matching", complete: Boolean(summary.latest_analysis) },
    { label: "Roadmap hoặc Mock Interview", complete: Boolean(summary.latest_roadmap || summary.latest_interview) }
  ];
  const completed = checks.filter((item) => item.complete).map((item) => item.label);
  const missing = checks.filter((item) => !item.complete).map((item) => item.label);
  return {
    completed,
    missing,
    percent: Math.round((completed.length / checks.length) * 100)
  };
}

function buildNextAction(summary: DashboardSummary): WorkspaceAction {
  if (!summary.has_career_profile) return { title: "Hoàn thiện hồ sơ nghề nghiệp", description: "Bổ sung vai trò mục tiêu, kỹ năng và mục tiêu để CareerOS có đủ ngữ cảnh.", href: "/profile", cta: "Cập nhật hồ sơ" };
  if (summary.resume_count === 0) return { title: "Tải CV lên", description: "Thêm CV PDF để hệ thống có dữ liệu hồ sơ cho bước Matching.", href: "/documents", cta: "Thêm CV" };
  if (summary.job_description_count === 0) return { title: "Thêm Job Description", description: "Lưu JD mục tiêu để đối chiếu CV với yêu cầu tuyển dụng cụ thể.", href: "/documents", cta: "Thêm JD" };
  if (!summary.latest_analysis) return { title: "Chạy Resume ↔ JD Matching", description: "Kiểm tra điểm phù hợp, skill gap và các gợi ý cải thiện CV.", href: "/analysis", cta: "Chạy Matching" };
  if (summary.has_new_resume_after_analysis || summary.should_rerun_analysis) return { title: "Chạy lại Matching", description: "CV hoặc tiến độ học tập đã thay đổi; hãy cập nhật kết quả phân tích.", href: "/analysis", cta: "Phân tích lại" };
  if (!summary.latest_roadmap) return { title: "Tạo Roadmap học tập", description: "Chuyển skill gap thành các bước học, bài thực hành và minh chứng CV.", href: "/roadmap", cta: "Tạo Roadmap" };
  if (summary.latest_interview?.status === "in_progress") return { title: "Hoàn thành Mock Interview hiện tại", description: "Tiếp tục các câu còn lại để có tổng kết phiên rõ ràng hơn.", href: "/interview", cta: "Tiếp tục phỏng vấn" };
  if (summary.latest_roadmap.total_items > 0 && summary.latest_roadmap.completed_items < summary.latest_roadmap.total_items) return { title: "Tiếp tục Roadmap", description: `Bạn đã hoàn thành ${summary.latest_roadmap.completed_items}/${summary.latest_roadmap.total_items} bước.`, href: "/roadmap", cta: "Mở Roadmap" };
  if (!summary.latest_interview) return { title: "Luyện Mock Interview", description: "Kiểm tra khả năng giải thích kỹ thuật theo vai trò và kỹ năng đang cải thiện.", href: "/interview", cta: "Bắt đầu luyện" };
  return { title: "Cập nhật CV và kiểm tra lại Matching", description: "Dùng kết quả Roadmap và Mock Interview để cải thiện CV trước lần phân tích tiếp theo.", href: "/documents", cta: "Quản lý CV/JD" };
}

function buildNextActionContext(summary: DashboardSummary, action: WorkspaceAction) {
  if (action.href === "/roadmap" && summary.latest_roadmap) {
    return `Roadmap gần nhất đã hoàn thành ${summary.latest_roadmap.completed_items}/${summary.latest_roadmap.total_items} bước.`;
  }
  if (action.href === "/analysis" && summary.latest_analysis) {
    return `Kết quả gần nhất đạt ${summary.latest_analysis.match_score}% phù hợp.`;
  }
  if (action.href === "/documents") {
    return `${summary.resume_count} CV và ${summary.job_description_count} JD đang được lưu.`;
  }
  if (action.href === "/interview" && summary.latest_interview) {
    return `Phiên gần nhất cho vai trò ${summary.latest_interview.target_role}: ${formatInterviewStatus(summary.latest_interview.status)}.`;
  }
  return `${summary.resume_count} CV · ${summary.job_description_count} JD · ${summary.latest_analysis ? "Đã có Matching" : "Chưa có Matching"}`;
}

function buildRecentActivities(summary: DashboardSummary): RecentActivity[] {
  const activities: RecentActivity[] = [];
  if (summary.latest_analysis) activities.push({ title: "Đã chạy Resume ↔ JD Matching", detail: `Điểm phù hợp ${summary.latest_analysis.match_score}%`, createdAt: summary.latest_analysis.created_at, href: "/analysis", marker: "M" });
  if (summary.latest_roadmap) activities.push({ title: "Đã tạo Roadmap", detail: `${summary.latest_roadmap.completed_items}/${summary.latest_roadmap.total_items} bước đã hoàn thành`, createdAt: summary.latest_roadmap.created_at, href: "/roadmap", marker: "R" });
  if (summary.latest_interview) activities.push({ title: summary.latest_interview.status === "finished" ? "Đã hoàn thành Mock Interview" : "Đã bắt đầu Mock Interview", detail: `${summary.latest_interview.target_role} · ${formatInterviewScore(summary.latest_interview.score)}`, createdAt: summary.latest_interview.created_at, href: "/interview", marker: "MI" });
  return activities.sort((left, right) => new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime()).slice(0, 4);
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}

function formatInterviewStatus(status: string) {
  if (status === "in_progress") return "Đang luyện";
  if (status === "finished") return "Đã hoàn thành";
  return "Chưa xác định";
}

function formatInterviewScore(score: number | null) {
  return score === null ? "Chưa có điểm" : `${score}/100`;
}
