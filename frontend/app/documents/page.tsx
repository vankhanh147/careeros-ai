"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import {
  createJobDescription,
  getMyJobDescriptions,
  getMyResumes,
  uploadResume,
  type JobDescription,
  type Resume
} from "@/lib/api/documents";
import { useAuth } from "@/lib/auth/AuthContext";

const MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024;

export default function DocumentsPage() {
  const router = useRouter();
  const { token, isAuthenticated, isLoading } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jdTitle, setJdTitle] = useState("");
  const [jdCompany, setJdCompany] = useState("");
  const [jdContent, setJdContent] = useState("");
  const [jdSourceUrl, setJdSourceUrl] = useState("");
  const [error, setError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isFetching, setIsFetching] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isSavingJd, setIsSavingJd] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    let isMounted = true;

    async function loadDocuments() {
      if (!token) {
        if (isMounted) {
          setIsFetching(false);
        }
        return;
      }

      try {
        setIsFetching(true);
        const [resumeList, jdList] = await Promise.all([
          getMyResumes(token),
          getMyJobDescriptions(token)
        ]);
        if (isMounted) {
          setResumes(resumeList);
          setJobDescriptions(jdList);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Không thể tải dữ liệu tài liệu.");
        }
      } finally {
        if (isMounted) {
          setIsFetching(false);
        }
      }
    }

    void loadDocuments();

    return () => {
      isMounted = false;
    };
  }, [token]);

  async function handleResumeUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!selectedFile) {
      setError("Vui lòng chọn file CV PDF.");
      return;
    }
    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setError("Chỉ hỗ trợ file PDF.");
      return;
    }
    if (selectedFile.size > MAX_RESUME_SIZE_BYTES) {
      setError("File PDF phải nhỏ hơn hoặc bằng 5MB.");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsUploading(true);

    try {
      const uploaded = await uploadResume(token, selectedFile);
      setResumes((current) => [uploaded, ...current]);
      setSelectedFile(null);
      event.currentTarget.reset();
      setStatusMessage("Đã upload CV PDF.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể upload CV.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleCreateJobDescription(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!jdContent.trim()) {
      setError("Nội dung Job Description không được để trống.");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsSavingJd(true);

    try {
      const created = await createJobDescription(token, {
        title: jdTitle.trim(),
        company: jdCompany.trim() || undefined,
        content: jdContent.trim(),
        source_url: jdSourceUrl.trim() || undefined
      });
      setJobDescriptions((current) => [created, ...current]);
      setJdTitle("");
      setJdCompany("");
      setJdContent("");
      setJdSourceUrl("");
      setStatusMessage("Đã lưu Job Description.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể lưu Job Description.");
    } finally {
      setIsSavingJd(false);
    }
  }

  if (isLoading || isFetching) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">Đang tải tài liệu...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">CV và Job Description</h1>
          </div>
          <Link
            href="/dashboard"
            className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10"
          >
            Về dashboard
          </Link>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-6 py-10 lg:grid-cols-2">
        <div className="rounded-lg border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Upload CV PDF</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Lưu CV PDF để chuẩn bị cho bước Resume ↔ Job Matching sau này. Giai đoạn này chưa phân tích nội dung CV.
          </p>
          <form onSubmit={handleResumeUpload} className="mt-6 space-y-4">
            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
              className="block w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200 file:mr-4 file:rounded-md file:border-0 file:bg-cyan-300 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-950"
            />
            <button
              type="submit"
              disabled={isUploading}
              className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isUploading ? "Đang upload..." : "Upload CV"}
            </button>
          </form>

          <div className="mt-8">
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">CV đã upload</h3>
            <div className="mt-4 space-y-3">
              {resumes.length === 0 ? (
                <p className="text-sm text-slate-400">Chưa có CV nào.</p>
              ) : (
                resumes.map((resume) => (
                  <div key={resume.id} className="rounded-md border border-white/10 bg-slate-950/60 p-4">
                    <p className="font-medium text-slate-100">{resume.file_name}</p>
                    <p className="mt-1 break-words text-xs text-slate-500">{resume.storage_path}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Lưu Job Description mục tiêu</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Paste JD từ vị trí bạn muốn apply. Giai đoạn này chỉ lưu dữ liệu, chưa chấm điểm matching.
          </p>
          <form onSubmit={handleCreateJobDescription} className="mt-6 space-y-4">
            <TextInput label="Tiêu đề vị trí" value={jdTitle} onChange={setJdTitle} placeholder="Backend Intern" required />
            <TextInput label="Công ty" value={jdCompany} onChange={setJdCompany} placeholder="Tên công ty nếu có" />
            <TextInput label="Nguồn JD" value={jdSourceUrl} onChange={setJdSourceUrl} placeholder="https://..." />
            <label className="block text-sm font-medium text-slate-200">
              Nội dung Job Description
              <textarea
                required
                rows={8}
                value={jdContent}
                onChange={(event) => setJdContent(event.target.value)}
                placeholder="Paste mô tả công việc, yêu cầu kỹ năng, trách nhiệm..."
                className="mt-2 w-full resize-y rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
              />
            </label>
            <button
              type="submit"
              disabled={isSavingJd}
              className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isSavingJd ? "Đang lưu..." : "Lưu Job Description"}
            </button>
          </form>
        </div>
      </section>

      <section className="mx-auto w-full max-w-6xl px-6 pb-10">
        {error ? <p className="mb-4 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
        {statusMessage ? (
          <p className="mb-4 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p>
        ) : null}

        <div className="rounded-lg border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Job Description đã lưu</h2>
          <div className="mt-4 space-y-3">
            {jobDescriptions.length === 0 ? (
              <p className="text-sm text-slate-400">Chưa có Job Description nào.</p>
            ) : (
              jobDescriptions.map((job) => (
                <article key={job.id} className="rounded-md border border-white/10 bg-slate-950/60 p-4">
                  <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                    <h3 className="font-medium text-slate-100">{job.title}</h3>
                    {job.company ? <p className="text-sm text-cyan-200">{job.company}</p> : null}
                  </div>
                  {job.source_url ? <p className="mt-1 break-words text-xs text-slate-500">{job.source_url}</p> : null}
                  <p className="mt-3 line-clamp-4 whitespace-pre-line text-sm leading-6 text-slate-300">{job.content}</p>
                </article>
              ))
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

function TextInput({
  label,
  value,
  onChange,
  placeholder,
  required = false
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  required?: boolean;
}) {
  return (
    <label className="block text-sm font-medium text-slate-200">
      {label}
      <input
        type="text"
        required={required}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
      />
    </label>
  );
}
