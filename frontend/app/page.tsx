const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen w-full max-w-5xl flex-col justify-center px-6 py-16">
        <p className="mb-4 text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">
          CareerOS AI
        </p>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl">
          Nền tảng AI hỗ trợ định hướng nghề nghiệp công nghệ.
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Scaffold Phase 2 đã sẵn sàng: Next.js frontend kết nối với FastAPI backend qua cấu hình môi trường.
        </p>
        <div className="mt-8 rounded-lg border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
          API base URL: <span className="font-mono text-cyan-200">{apiBaseUrl}</span>
        </div>
      </section>
    </main>
  );
}
