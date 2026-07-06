"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { useAuth } from "@/lib/auth/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const canSubmit = email.trim().length > 0 && password.length >= 8 && !isSubmitting;

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await login({ email: email.trim(), password });
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Đăng nhập không thành công. Vui lòng kiểm tra email, mật khẩu hoặc kết nối backend.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-start justify-center bg-slate-950 px-6 pb-12 pt-16 text-white sm:pt-20 lg:pt-24">
      <section className="w-full max-w-md">
        <p className="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
        <h1 className="text-3xl font-semibold tracking-tight">Đăng nhập</h1>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Tiếp tục vào dashboard để quản lý hành trình phát triển nghề nghiệp công nghệ của bạn.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-200">Email</label>
            <input id="email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-md border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300" placeholder="you@example.com" />
            <p className="mt-2 text-xs text-slate-500">Dùng email bạn đã đăng ký CareerOS AI.</p>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-200">Mật khẩu</label>
            <input id="password" type="password" required minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-md border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300" placeholder="Ít nhất 8 ký tự" />
            <p className="mt-2 text-xs text-slate-500">Nhập mật khẩu của tài khoản CareerOS AI.</p>
          </div>

          {error ? <p className="rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}

          <button type="submit" disabled={!canSubmit} className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70">
            {isSubmitting ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>
        </form>

        <p className="mt-6 text-sm text-slate-300">
          Chưa có tài khoản? <Link href="/register" className="font-semibold text-cyan-200 hover:text-cyan-100">Đăng ký ngay</Link>
        </p>
      </section>
    </main>
  );
}
