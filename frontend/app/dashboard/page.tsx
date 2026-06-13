"use client";

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
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-5">
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

      <section className="mx-auto w-full max-w-6xl px-6 py-10">
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

        <div className="mt-6 rounded-lg border border-dashed border-white/15 p-6">
          <h2 className="text-lg font-semibold">Core MVP sẽ được xây dựng tiếp tại đây</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
            Phase này chỉ thiết lập authentication và dashboard shell. Career profile, resume, job description và AI workflows sẽ được triển khai ở các bước sau.
          </p>
        </div>
      </section>
    </main>
  );
}
