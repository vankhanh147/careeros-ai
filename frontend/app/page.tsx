import Link from "next/link";

const productSignals = [
  { label: "Điểm phù hợp", value: "78%" },
  { label: "Khoảng trống ưu tiên", value: "JWT · Docker" },
  { label: "Hành động tiếp theo", value: "Tạo roadmap 4 tuần" }
];

export default function Home() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center px-4 py-12 sm:px-6 sm:py-16">
        <div className="grid items-center gap-10 lg:grid-cols-[1.08fr_0.92fr] lg:gap-14">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl">
              Biến CV và mục tiêu nghề nghiệp thành kế hoạch phát triển rõ ràng.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg sm:leading-8">
              So khớp CV với JD, nhận diện khoảng trống kỹ năng, cải thiện cách trình bày kinh nghiệm và luyện phỏng vấn theo đúng vai trò bạn đang hướng tới.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href="/register" className="inline-flex justify-center rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200">
                Bắt đầu miễn phí
              </Link>
              <Link href="/login" className="inline-flex justify-center rounded-md border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
                Đăng nhập
              </Link>
            </div>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              AI giải thích được, không tự bịa kinh nghiệm và không phụ thuộc LLM API.
            </p>
          </div>

          <ProductPreview />
        </div>

        <div className="mt-12 border-t border-white/10 pt-8">
          <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">Bắt đầu trong 3 bước</p>
              <h2 className="mt-2 text-xl font-semibold text-slate-100">Từ hồ sơ hiện tại đến hành động tiếp theo</h2>
            </div>
            <p className="max-w-md text-sm leading-6 text-slate-400">Mỗi bước tạo dữ liệu cho bước kế tiếp, giúp kết quả ngày càng sát mục tiêu của bạn.</p>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <OnboardingStep step="1" title="Hoàn thiện hồ sơ" description="Nhập vai trò mục tiêu, kỹ năng, kinh nghiệm và thời gian dự kiến để hệ thống hiểu bối cảnh của bạn." />
            <OnboardingStep step="2" title="Thêm CV và JD" description="Tải lên CV PDF, sau đó dán hoặc tải lên JD của vị trí bạn muốn ứng tuyển." />
            <OnboardingStep step="3" title="Phân tích và luyện tập" description="Chạy Resume ↔ JD Matching, tạo Roadmap và luyện Mock Interview theo các khoảng trống đã phát hiện." />
          </div>
        </div>
      </section>
    </main>
  );
}

function ProductPreview() {
  return (
    <aside className="min-w-0 rounded-lg border border-cyan-300/20 bg-white/5 p-4 shadow-2xl shadow-cyan-950/20 sm:p-5">
      <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-300">Không gian nghề nghiệp</p>
          <h2 className="mt-2 text-lg font-semibold text-slate-100">Backend Developer</h2>
        </div>
        <span className="shrink-0 rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-xs font-medium text-emerald-200">
          Đã phân tích
        </span>
      </div>

      <div className="mt-4 grid gap-3">
        {productSignals.map((signal) => (
          <div key={signal.label} className="min-w-0 rounded-md border border-white/10 bg-slate-950/70 p-4">
            <p className="text-xs text-slate-500">{signal.label}</p>
            <p className="mt-1 break-words text-sm font-semibold text-slate-100">{signal.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-md border border-cyan-300/20 bg-cyan-300/10 p-4">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-200">Gợi ý ưu tiên</p>
        <p className="mt-2 text-sm leading-6 text-cyan-50">
          Bổ sung minh chứng về xác thực API và hoàn thành một bài thực hành triển khai bằng Docker.
        </p>
      </div>
    </aside>
  );
}

function OnboardingStep({ step, title, description }: { step: string; title: string; description: string }) {
  return (
    <article className="min-w-0 rounded-lg border border-white/10 bg-white/5 p-5">
      <div className="flex items-center gap-3">
        <p className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-cyan-300 text-sm font-bold text-slate-950">{step}</p>
        <h3 className="text-base font-semibold text-slate-100">{title}</h3>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-300">{description}</p>
    </article>
  );
}
