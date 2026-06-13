import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen w-full max-w-5xl flex-col justify-center px-6 py-16">
        <p className="mb-4 text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl">
          Nền tảng AI hỗ trợ định hướng nghề nghiệp công nghệ.
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Đăng ký, đăng nhập và bắt đầu xây dựng career operating system cá nhân của bạn.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/register"
            className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
          >
            Tạo tài khoản
          </Link>
          <Link
            href="/login"
            className="rounded-md border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
          >
            Đăng nhập
          </Link>
        </div>
      </section>
    </main>
  );
}
