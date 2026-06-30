"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { getMyCareerProfile, updateMyCareerProfile, type CareerProfilePayload } from "@/lib/api/careerProfile";
import { useAuth } from "@/lib/auth/AuthContext";

const emptyProfile: CareerProfilePayload = {
  target_role: "",
  current_level: "",
  skills: "",
  experience_summary: "",
  projects_summary: "",
  career_goal: "",
  timeline: ""
};

export default function ProfilePage() {
  const router = useRouter();
  const { token, isAuthenticated, isLoading } = useAuth();
  const [form, setForm] = useState<CareerProfilePayload>(emptyProfile);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [isFetching, setIsFetching] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const hasAnyProfileData = Object.values(form).some((value) => value.trim().length > 0);

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
        const profile = await getMyCareerProfile(token);
        if (isMounted && profile) {
          setForm({
            target_role: profile.target_role,
            current_level: profile.current_level,
            skills: profile.skills,
            experience_summary: profile.experience_summary,
            projects_summary: profile.projects_summary,
            career_goal: profile.career_goal,
            timeline: profile.timeline
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
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">Đang tải hồ sơ nghề nghiệp...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Hồ sơ nghề nghiệp</h1>
          </div>
          <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
            Về dashboard
          </Link>
        </div>
      </header>

      <section className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6">
        <div className="mb-8 max-w-3xl">
          <h2 className="text-3xl font-semibold tracking-tight">Thông tin định hướng hiện tại</h2>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Đây là nền dữ liệu để CareerOS AI hiểu mục tiêu, kỹ năng, kinh nghiệm, dự án và thời gian dự kiến của bạn trước khi tạo roadmap hoặc mô phỏng phỏng vấn.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          {!hasAnyProfileData ? (
            <div className="rounded-md border border-cyan-300/20 bg-cyan-300/10 p-4 text-sm leading-6 text-cyan-50">
              Bắt đầu bằng vai trò mục tiêu và kỹ năng hiện có. Những thông tin này giúp CareerOS AI tạo Roadmap và Mock Interview sát hơn.
            </div>
          ) : null}

          <div className="grid gap-5 md:grid-cols-2">
            <TextInput label="Vai trò mục tiêu" value={form.target_role} onChange={(value) => updateField("target_role", value)} placeholder="Backend Intern, Frontend Developer, AI Engineer..." hint="Ví dụ: Backend Intern trong 3 tháng tới." />
            <TextInput label="Trình độ hiện tại" value={form.current_level} onChange={(value) => updateField("current_level", value)} placeholder="Sinh viên, Fresher, Junior, Career Switcher..." hint="Giúp hệ thống điều chỉnh độ khó của Roadmap và Mock Interview." />
          </div>

          <TextArea label="Kỹ năng hiện có" value={form.skills} onChange={(value) => updateField("skills", value)} placeholder="Ví dụ: Python, FastAPI, PostgreSQL, React, TypeScript..." hint="Liệt kê bằng dấu phẩy để matcher đọc dễ hơn." />
          <TextArea label="Tóm tắt kinh nghiệm" value={form.experience_summary} onChange={(value) => updateField("experience_summary", value)} placeholder="Bạn đã học/làm gì, mức độ kinh nghiệm, môi trường làm việc hoặc học tập." />
          <TextArea label="Tóm tắt dự án" value={form.projects_summary} onChange={(value) => updateField("projects_summary", value)} placeholder="Các dự án nổi bật, công nghệ sử dụng, vai trò của bạn và kết quả đạt được." />
          <TextArea label="Mục tiêu nghề nghiệp" value={form.career_goal} onChange={(value) => updateField("career_goal", value)} placeholder="Bạn muốn đạt vị trí hoặc vai trò nào và vì sao?" />
          <TextInput label="Thời gian dự kiến" value={form.timeline} onChange={(value) => updateField("timeline", value)} placeholder="Ví dụ: 3 tháng để sẵn sàng Backend Intern" />

          {error ? <p className="rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
          {statusMessage ? <p className="rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}

          <button type="submit" disabled={isSaving || !hasAnyProfileData} className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70">
            {isSaving ? "Đang lưu hồ sơ..." : "Lưu hồ sơ"}
          </button>
        </form>
      </section>
    </main>
  );
}

function TextInput({ label, value, onChange, placeholder, hint }: { label: string; value: string; onChange: (value: string) => void; placeholder: string; hint?: string }) {
  return (
    <label className="block min-w-0 text-sm font-medium text-slate-200">
      {label}
      <input type="text" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className="mt-2 w-full min-w-0 rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300" />
      {hint ? <span className="mt-2 block text-xs leading-5 text-slate-500">{hint}</span> : null}
    </label>
  );
}

function TextArea({ label, value, onChange, placeholder, hint }: { label: string; value: string; onChange: (value: string) => void; placeholder: string; hint?: string }) {
  return (
    <label className="block min-w-0 text-sm font-medium text-slate-200">
      {label}
      <textarea value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} rows={4} className="mt-2 w-full min-w-0 resize-y rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300" />
      {hint ? <span className="mt-2 block text-xs leading-5 text-slate-500">{hint}</span> : null}
    </label>
  );
}
