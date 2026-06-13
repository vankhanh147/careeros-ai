"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/lib/auth/AuthContext";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  if (isLoading || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">Đang tải dashboard...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Dashboard</h1>
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
        <div className="rounded-lg border border-white/10 bg-white/5 p-6">
          <p className="text-sm font-medium text-cyan-200">Tài khoản đang đăng nhập</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight">{user.full_name}</h2>
          <dl className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-md border border-white/10 bg-slate-950/60 p-4">
              <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">Email</dt>
              <dd className="mt-2 break-words text-sm font-medium text-slate-100">{user.email}</dd>
            </div>
            <div className="rounded-md border border-white/10 bg-slate-950/60 p-4">
              <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">Role</dt>
              <dd className="mt-2 text-sm font-medium text-slate-100">{user.role}</dd>
            </div>
            <div className="rounded-md border border-white/10 bg-slate-950/60 p-4">
              <dt className="text-xs uppercase tracking-[0.18em] text-slate-500">Trạng thái</dt>
              <dd className="mt-2 text-sm font-medium text-slate-100">
                {user.is_active ? "Đang hoạt động" : "Không hoạt động"}
              </dd>
            </div>
          </dl>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-2 xl:grid-cols-5">
          <DashboardActionCard
            title="Hồ sơ nghề nghiệp"
            description="Cập nhật mục tiêu, kỹ năng, kinh nghiệm và timeline để chuẩn bị cho Career Diagnosis và roadmap cá nhân hóa."
            href="/profile"
            cta="Cập nhật hồ sơ"
          />
          <DashboardActionCard
            title="CV và Job Description"
            description="Upload CV PDF và lưu JD mục tiêu. Đây là dữ liệu nền cho Resume ↔ Job Matching ở phase AI MVP."
            href="/documents"
            cta="Quản lý CV và JD"
          />
          <DashboardActionCard
            title="Resume ↔ Job Matching"
            description="Chọn CV và Job Description đã lưu để nhận match score, skill gap và gợi ý cải thiện có thể giải thích."
            href="/analysis"
            cta="Phân tích matching"
          />
          <DashboardActionCard
            title="Personalized Roadmap"
            description="Tạo roadmap học tập ngắn hạn từ career profile, analysis gần đây và skill gap đang cần ưu tiên."
            href="/roadmap"
            cta="Tạo roadmap"
          />
          <DashboardActionCard
            title="Mock Interview AI"
            description="Luyện phỏng vấn kỹ thuật bằng question bank theo target role, skill gap và feedback rule-based."
            href="/interview"
            cta="Luyện phỏng vấn"
          />
        </div>
      </section>
    </main>
  );
}

function DashboardActionCard({
  title,
  description,
  href,
  cta
}: {
  title: string;
  description: string;
  href: string;
  cta: string;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-6">
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-slate-300">{description}</p>
      <Link
        href={href}
        className="mt-5 inline-flex rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
      >
        {cta}
      </Link>
    </div>
  );
}