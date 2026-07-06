"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { getMyCareerProfile, updateMyCareerProfile, type CareerProfilePayload } from "@/lib/api/careerProfile";
import { useAuth } from "@/lib/auth/AuthContext";
import { PageLoading, buttonStyles } from "@/components/ui/ProductUI";

const emptyProfile: CareerProfilePayload = {
  target_role: "",
  current_level: "",
  skills: "",
  experience_summary: "",
  projects_summary: "",
  career_goal: "",
  timeline: ""
};

const PROFILE_COMPLETION_FIELDS: Array<{ key: keyof CareerProfilePayload; label: string }> = [
  { key: "target_role", label: "Vai trò mục tiêu" },
  { key: "current_level", label: "Trình độ hiện tại" },
  { key: "skills", label: "Kỹ năng hiện có" },
  { key: "experience_summary", label: "Tóm tắt kinh nghiệm" },
  { key: "projects_summary", label: "Tóm tắt dự án" },
  { key: "career_goal", label: "Mục tiêu nghề nghiệp" },
  { key: "timeline", label: "Thời gian dự kiến" }
];

export default function ProfilePage() {
  const router = useRouter();
  const { token, isAuthenticated, isLoading } = useAuth();
  const [form, setForm] = useState<CareerProfilePayload>(emptyProfile);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [isFetching, setIsFetching] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const completedFields = PROFILE_COMPLETION_FIELDS.filter(({ key }) => form[key].trim().length > 0);
  const missingFields = PROFILE_COMPLETION_FIELDS.filter(({ key }) => form[key].trim().length === 0);
  const completionPercent = Math.round((completedFields.length / PROFILE_COMPLETION_FIELDS.length) * 100);
  const hasAnyProfileData = completedFields.length > 0;

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    let isMounted = true;

    async function loadProfile() {
      if (!token) {
        if (isMounted) {
          setIsFetching(false);
        }
        return;
      }

      try {
        setIsFetching(true);
        const profileData = await getMyCareerProfile(token);
        if (isMounted && profileData) {
          setForm({
            target_role: profileData.target_role,
            current_level: profileData.current_level,
            skills: profileData.skills,
            experience_summary: profileData.experience_summary,
            projects_summary: profileData.projects_summary,
            career_goal: profileData.career_goal,
            timeline: profileData.timeline
          });
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Không thể tải hồ sơ nghề nghiệp. Vui lòng kiểm tra kết nối backend.");
        }
      } finally {
        if (isMounted) {
          setIsFetching(false);
        }
      }
    }

    void loadProfile();

    return () => {
      isMounted = false;
    };
  }, [token]);

  function updateField(field: keyof CareerProfilePayload, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
    setStatusMessage("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsSaving(true);

    try {
      await updateMyCareerProfile(token, form);
      setStatusMessage("Đã lưu hồ sơ nghề nghiệp.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể lưu hồ sơ nghề nghiệp. Vui lòng thử lại.");
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading || isFetching) {
    return <PageLoading title="Đang tải hồ sơ nghề nghiệp..." description="CareerOS AI đang đồng bộ thông tin hồ sơ của bạn." />;
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Hồ sơ nghề nghiệp</h1>
          </div>
          <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-center text-sm font-semibold transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60">
            Về Dashboard
          </Link>
        </div>
      </header>

      <section className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6">
        <div className="mb-8 max-w-3xl">
          <h2 className="text-3xl font-semibold tracking-tight">Thông tin định hướng hiện tại</h2>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Cung cấp đủ ngữ cảnh để CareerOS AI hiểu mục tiêu, kỹ năng và kinh nghiệm của bạn trước khi tạo Roadmap hoặc Mock Interview.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-7 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-7">
          <ProfileCompletion
            completedFields={completedFields.map((field) => field.label)}
            missingFields={missingFields.map((field) => field.label)}
            percent={completionPercent}
          />

          {!hasAnyProfileData ? (
            <div className="rounded-md border border-cyan-300/20 bg-cyan-300/10 p-4 text-sm leading-6 text-cyan-50">
              Bắt đầu bằng vai trò mục tiêu và kỹ năng hiện có. Bạn có thể bổ sung các phần còn lại sau.
            </div>
          ) : null}

          <div className="grid gap-6 md:grid-cols-2">
            <TextInput
              id="target-role"
              label="Vai trò mục tiêu"
              tooltip="Đây là vị trí bạn muốn ứng tuyển, ví dụ Backend Intern, Frontend Intern, AI Engineer hoặc Data Analyst."
              value={form.target_role}
              onChange={(value) => updateField("target_role", value)}
              placeholder="Ví dụ: Backend Intern hoặc Frontend React Developer"
            />
            <TextInput
              id="current-level"
              label="Trình độ hiện tại"
              tooltip="Chọn cách mô tả gần nhất với kinh nghiệm hiện tại để hệ thống điều chỉnh độ khó phù hợp."
              value={form.current_level}
              onChange={(value) => updateField("current_level", value)}
              placeholder="Ví dụ: Sinh viên năm 4, Fresher hoặc Junior"
            />
          </div>

          <TextArea
            id="skills"
            label="Kỹ năng hiện có"
            tooltip="Liệt kê công nghệ và kỹ năng bạn đã thực sự học hoặc sử dụng. Phân tách bằng dấu phẩy để hệ thống đọc rõ hơn."
            value={form.skills}
            onChange={(value) => updateField("skills", value)}
            placeholder="Ví dụ: C#, ASP.NET Core, PostgreSQL, Docker, Git, React"
            hint="Chỉ liệt kê những kỹ năng bạn có thể giải thích hoặc chứng minh bằng bài tập, dự án hay kinh nghiệm."
            rows={3}
          />
          <TextArea
            id="experience-summary"
            label="Tóm tắt kinh nghiệm"
            tooltip="Mô tả ngắn những gì bạn đã làm, trách nhiệm kỹ thuật và công nghệ đã sử dụng."
            value={form.experience_summary}
            onChange={(value) => updateField("experience_summary", value)}
            placeholder="Ví dụ: Thực hiện dự án SmartStay bằng ASP.NET Core và React, xây dựng REST API, JWT Authentication và triển khai lên Render."
            rows={5}
          />
          <TextArea
            id="projects-summary"
            label="Tóm tắt dự án"
            tooltip="Nêu tên dự án, mục tiêu, vai trò của bạn, công nghệ chính và kết quả có thể kiểm chứng."
            value={form.projects_summary}
            onChange={(value) => updateField("projects_summary", value)}
            placeholder={"Ví dụ: CareerOS AI – Nền tảng AI hỗ trợ định hướng nghề nghiệp.\nVai trò: Backend Developer. Công nghệ: FastAPI, PostgreSQL, Supabase."}
            rows={5}
          />
          <TextArea
            id="career-goal"
            label="Mục tiêu nghề nghiệp"
            tooltip="Mô tả vị trí bạn muốn đạt được và hướng phát triển sau đó. Mục tiêu cụ thể giúp Roadmap sát hơn."
            value={form.career_goal}
            onChange={(value) => updateField("career_goal", value)}
            placeholder="Ví dụ: Ứng tuyển Backend Intern trong năm nay và phát triển lên Backend Engineer."
            rows={4}
          />
          <TextInput
            id="timeline"
            label="Thời gian dự kiến"
            tooltip="Khoảng thời gian bạn muốn dành để chuẩn bị cho mục tiêu hiện tại. Hệ thống dùng dữ liệu này để chia Roadmap."
            value={form.timeline}
            onChange={(value) => updateField("timeline", value)}
            placeholder="Ví dụ: 3 tháng để sẵn sàng Backend Intern"
          />

          <div aria-live="polite" className="space-y-3">
            {error ? <p className="rounded-md border border-red-300/15 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
            {statusMessage ? <p className="rounded-md border border-emerald-300/15 bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}
          </div>

          <div className="flex border-t border-white/10 pt-6 sm:justify-end">
            <button
              type="submit"
              disabled={isSaving || !hasAnyProfileData}
              className={buttonStyles("primary", "w-full px-6 py-3 sm:w-auto")}
            >
              <SaveIcon />
              {isSaving ? "Đang lưu hồ sơ..." : "Lưu hồ sơ"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

function ProfileCompletion({ completedFields, missingFields, percent }: { completedFields: string[]; missingFields: string[]; percent: number }) {
  return (
    <section className="rounded-lg border border-cyan-300/20 bg-slate-950/60 p-5" aria-labelledby="profile-completion-title">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-300">Tiến độ hồ sơ</p>
          <h2 id="profile-completion-title" className="mt-2 text-lg font-semibold text-slate-100">Hoàn thành hồ sơ</h2>
        </div>
        <p className="text-2xl font-semibold text-cyan-200">{percent}%</p>
      </div>

      <div
        className="mt-4 h-2 overflow-hidden rounded-full bg-white/10"
        role="progressbar"
        aria-label="Mức độ hoàn thành hồ sơ"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
      >
        <div className="h-full rounded-full bg-cyan-300 transition-[width] duration-300" style={{ width: `${percent}%` }} />
      </div>
      <p className="mt-2 text-xs text-slate-500">{completedFields.length}/{PROFILE_COMPLETION_FIELDS.length} mục đã có thông tin</p>

      <div className="mt-5 grid gap-5 sm:grid-cols-2">
        <CompletionList title="Đã hoàn thành" items={completedFields} completed />
        <CompletionList title="Còn thiếu" items={missingFields} />
      </div>
    </section>
  );
}

function CompletionList({ title, items, completed = false }: { title: string; items: string[]; completed?: boolean }) {
  return (
    <div className="min-w-0">
      <h3 className={`text-sm font-semibold ${completed ? "text-emerald-200" : "text-slate-300"}`}>{title}</h3>
      {items.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm text-slate-300">
          {items.map((item) => (
            <li key={item} className="flex min-w-0 items-start gap-2">
              <span aria-hidden="true" className={`mt-0.5 shrink-0 ${completed ? "text-emerald-300" : "text-slate-500"}`}>
                {completed ? "✓" : "•"}
              </span>
              <span className="break-words">{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-slate-500">{completed ? "Chưa có mục nào." : "Hồ sơ đã đủ các mục."}</p>
      )}
    </div>
  );
}

type FieldProps = {
  id: string;
  label: string;
  tooltip: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  hint?: string;
};

function TextInput({ id, label, tooltip, value, onChange, placeholder, hint }: FieldProps) {
  const hintId = hint ? `${id}-hint` : undefined;
  return (
    <div className="min-w-0">
      <FieldLabel id={id} label={label} tooltip={tooltip} />
      <input
        id={id}
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        aria-describedby={hintId}
        className="mt-2 w-full min-w-0 rounded-md border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 hover:border-white/20 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/20"
      />
      {hint ? <p id={hintId} className="mt-2 text-xs leading-5 text-slate-500">{hint}</p> : null}
    </div>
  );
}

function TextArea({ id, label, tooltip, value, onChange, placeholder, hint, rows = 4 }: FieldProps & { rows?: number }) {
  const hintId = hint ? `${id}-hint` : undefined;
  return (
    <div className="min-w-0">
      <FieldLabel id={id} label={label} tooltip={tooltip} />
      <textarea
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        aria-describedby={hintId}
        rows={rows}
        className="mt-2 w-full min-w-0 resize-y rounded-md border border-white/10 bg-slate-950/70 px-4 py-3 leading-6 text-white outline-none transition placeholder:text-slate-500 hover:border-white/20 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/20"
      />
      {hint ? <p id={hintId} className="mt-2 text-xs leading-5 text-slate-500">{hint}</p> : null}
    </div>
  );
}

function FieldLabel({ id, label, tooltip }: { id: string; label: string; tooltip: string }) {
  return (
    <div className="flex items-center gap-2">
      <label htmlFor={id} className="text-sm font-medium text-slate-200">{label}</label>
      <InfoTooltip id={`${id}-tooltip`} content={tooltip} />
    </div>
  );
}

function InfoTooltip({ id, content }: { id: string; content: string }) {
  return (
    <span className="group relative inline-flex">
      <button
        type="button"
        aria-label="Xem hướng dẫn"
        aria-describedby={id}
        className="flex h-5 w-5 items-center justify-center rounded-full border border-white/15 text-xs font-semibold text-slate-400 transition hover:border-cyan-300/40 hover:text-cyan-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60"
      >
        ?
      </button>
      <span
        id={id}
        role="tooltip"
        className="pointer-events-none absolute left-0 top-7 z-20 w-64 max-w-[calc(100vw-3rem)] rounded-md border border-white/10 bg-slate-900 p-3 text-xs font-normal leading-5 text-slate-200 opacity-0 shadow-xl transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
      >
        {content}
      </span>
    </span>
  );
}

function SaveIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z" />
      <path d="M17 21v-8H7v8M7 3v5h8" />
    </svg>
  );
}
