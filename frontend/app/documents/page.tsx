"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import {
  createJobDescription,
  deleteJobDescription,
  deleteResume,
  getMyJobDescriptions,
  getMyResumes,
  updateJobDescription,
  uploadJobDescription,
  uploadResume,
  type JobDescription,
  type Resume
} from "@/lib/api/documents";
import { useAuth } from "@/lib/auth/AuthContext";

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;

export default function DocumentsPage() {
  const router = useRouter();
  const { token, isAuthenticated, isLoading } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([]);
  const [selectedResumeFile, setSelectedResumeFile] = useState<File | null>(null);
  const [resumeFileInputKey, setResumeFileInputKey] = useState(0);
  const [selectedJdFile, setSelectedJdFile] = useState<File | null>(null);
  const [jdFileInputKey, setJdFileInputKey] = useState(0);
  const [editingJobDescriptionId, setEditingJobDescriptionId] = useState<number | null>(null);
  const [jdTitle, setJdTitle] = useState("");
  const [jdCompany, setJdCompany] = useState("");
  const [jdContent, setJdContent] = useState("");
  const [jdSourceUrl, setJdSourceUrl] = useState("");
  const [jdUploadTitle, setJdUploadTitle] = useState("");
  const [jdUploadCompany, setJdUploadCompany] = useState("");
  const [error, setError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isFetching, setIsFetching] = useState(true);
  const [isUploadingResume, setIsUploadingResume] = useState(false);
  const [isUploadingJd, setIsUploadingJd] = useState(false);
  const [isSavingJd, setIsSavingJd] = useState(false);
  const [deletingResumeId, setDeletingResumeId] = useState<number | null>(null);
  const [deletingJobDescriptionId, setDeletingJobDescriptionId] = useState<number | null>(null);
  const canUploadResume = Boolean(selectedResumeFile) && !isUploadingResume;
  const canUploadJd = Boolean(selectedJdFile) && !isUploadingJd;
  const canSaveJd = jdTitle.trim().length > 0 && jdContent.trim().length > 0 && !isSavingJd;

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
          setError(err instanceof Error ? err.message : "Không thể tải dữ liệu tài liệu. Vui lòng kiểm tra kết nối backend.");
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
    if (!selectedResumeFile) {
      setError("Vui lòng chọn file CV PDF.");
      return;
    }
    if (!selectedResumeFile.name.toLowerCase().endsWith(".pdf")) {
      setError("CV chỉ hỗ trợ file PDF.");
      return;
    }
    if (selectedResumeFile.size > MAX_FILE_SIZE_BYTES) {
      setError("File CV phải nhỏ hơn hoặc bằng 5MB.");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsUploadingResume(true);

    try {
      const uploaded = await uploadResume(token, selectedResumeFile);
      setResumes((current) => [uploaded, ...current]);
      setSelectedResumeFile(null);
      setResumeFileInputKey((current) => current + 1);
      setStatusMessage("Đã upload CV PDF.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể upload CV.");
    } finally {
      setIsUploadingResume(false);
    }
  }

  async function handleDeleteResume(resume: Resume) {
    if (!token) {
      router.replace("/login");
      return;
    }
    const confirmed = window.confirm(`Xóa CV "${resume.file_name}"? File local cũng sẽ bị xóa nếu còn tồn tại.`);
    if (!confirmed) return;

    setError("");
    setStatusMessage("");
    setDeletingResumeId(resume.id);
    try {
      await deleteResume(token, resume.id);
      setResumes((current) => current.filter((item) => item.id !== resume.id));
      setStatusMessage("Đã xóa CV.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể xóa CV.");
    } finally {
      setDeletingResumeId(null);
    }
  }

  async function handleJobDescriptionUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!selectedJdFile) {
      setError("Vui lòng chọn file JD PDF hoặc TXT.");
      return;
    }
    const lowerName = selectedJdFile.name.toLowerCase();
    if (!lowerName.endsWith(".pdf") && !lowerName.endsWith(".txt")) {
      setError("JD upload hiện hỗ trợ file PDF hoặc TXT.");
      return;
    }
    if (selectedJdFile.size > MAX_FILE_SIZE_BYTES) {
      setError("File JD phải nhỏ hơn hoặc bằng 5MB.");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsUploadingJd(true);

    try {
      const uploaded = await uploadJobDescription(token, {
        file: selectedJdFile,
        title: jdUploadTitle.trim() || undefined,
        company: jdUploadCompany.trim() || undefined
      });
      setJobDescriptions((current) => [uploaded, ...current]);
      setSelectedJdFile(null);
      setJdUploadTitle("");
      setJdUploadCompany("");
      setJdFileInputKey((current) => current + 1);
      setStatusMessage("Đã upload và đọc nội dung JD.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể upload JD.");
    } finally {
      setIsUploadingJd(false);
    }
  }

  async function handleSaveJobDescription(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!jdTitle.trim()) {
      setError("Tiêu đề JD không được để trống.");
      return;
    }
    if (!jdContent.trim()) {
      setError("Nội dung JD không được để trống.");
      return;
    }

    setError("");
    setStatusMessage("");
    setIsSavingJd(true);

    try {
      const payload = {
        title: jdTitle.trim(),
        company: jdCompany.trim() || undefined,
        content: jdContent.trim(),
        source_url: jdSourceUrl.trim() || undefined
      };
      if (editingJobDescriptionId) {
        const updated = await updateJobDescription(token, editingJobDescriptionId, payload);
        setJobDescriptions((current) => current.map((job) => (job.id === updated.id ? updated : job)));
        setStatusMessage("Đã cập nhật JD.");
      } else {
        const created = await createJobDescription(token, payload);
        setJobDescriptions((current) => [created, ...current]);
        setStatusMessage("Đã lưu JD.");
      }
      resetJobDescriptionForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể lưu JD.");
    } finally {
      setIsSavingJd(false);
    }
  }

  function startEditJobDescription(job: JobDescription) {
    setEditingJobDescriptionId(job.id);
    setJdTitle(job.title);
    setJdCompany(job.company ?? "");
    setJdContent(job.content);
    setJdSourceUrl(job.source_url ?? "");
    setError("");
    setStatusMessage("Đang chỉnh sửa JD đã chọn.");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function resetJobDescriptionForm() {
    setEditingJobDescriptionId(null);
    setJdTitle("");
    setJdCompany("");
    setJdContent("");
    setJdSourceUrl("");
  }

  async function handleDeleteJobDescription(job: JobDescription) {
    if (!token) {
      router.replace("/login");
      return;
    }
    const confirmed = window.confirm(`Xóa JD "${job.title}"? Các phân tích cũ liên quan có thể không còn dùng lại được.`);
    if (!confirmed) return;

    setError("");
    setStatusMessage("");
    setDeletingJobDescriptionId(job.id);
    try {
      await deleteJobDescription(token, job.id);
      setJobDescriptions((current) => current.filter((item) => item.id !== job.id));
      if (editingJobDescriptionId === job.id) {
        resetJobDescriptionForm();
      }
      setStatusMessage("Đã xóa JD.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể xóa JD.");
    } finally {
      setDeletingJobDescriptionId(null);
    }
  }

  if (isLoading || isFetching) {
    return (
      <main className="flex min-h-screen items-center justify-center overflow-x-hidden bg-slate-950 px-6 text-white">
        <p className="text-sm text-slate-300">Đang tải tài liệu...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-slate-950 text-white">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="min-w-0">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">CareerOS AI</p>
            <h1 className="mt-1 text-xl font-semibold">Quản lý CV và JD</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/analysis" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              Phân tích matching
            </Link>
            <Link href="/dashboard" className="rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10">
              Về dashboard
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid w-full min-w-0 max-w-6xl grid-cols-1 gap-6 px-4 py-10 sm:px-6 lg:grid-cols-2">
        <div className="min-w-0 overflow-hidden rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Upload CV PDF</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Lưu CV PDF để hệ thống trích xuất text và chạy Resume ↔ JD Matching. File tối đa 5MB.
          </p>
          <form onSubmit={handleResumeUpload} className="mt-6 space-y-4">
            <input
              key={resumeFileInputKey}
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setSelectedResumeFile(event.target.files?.[0] ?? null)}
              className="block w-full min-w-0 max-w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200 file:mr-4 file:rounded-md file:border-0 file:bg-cyan-300 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-950"
            />
            <p className="text-xs leading-5 text-slate-500">Chỉ nhận PDF tối đa 5MB. File này sẽ được dùng để trích xuất text khi chạy analysis.</p>
            <button type="submit" disabled={!canUploadResume} className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70">
              {isUploadingResume ? "Đang upload CV..." : "Upload CV"}
            </button>
          </form>

          <div className="mt-8">
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">CV đã upload</h3>
            <div className="mt-4 space-y-3">
              {resumes.length === 0 ? (
                <p className="text-sm leading-6 text-slate-400">Chưa có CV nào. Upload CV PDF để bắt đầu phân tích matching.</p>
              ) : (
                resumes.map((resume) => (
                  <div key={resume.id} className="min-w-0 overflow-hidden rounded-md border border-white/10 bg-slate-950/60 p-4">
                    <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0 flex-1">
                        <p className="break-words text-sm font-medium leading-6 text-slate-100">{resume.file_name}</p>
                        <p title={resume.storage_path} className="mt-1 break-all text-xs leading-5 text-slate-500">{resume.storage_path}</p>
                      </div>
                      <button type="button" onClick={() => void handleDeleteResume(resume)} disabled={deletingResumeId === resume.id} className="w-full shrink-0 rounded-md border border-red-300/30 px-3 py-2 text-sm font-semibold text-red-200 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto">
                        {deletingResumeId === resume.id ? "Đang xóa..." : "Xóa CV"}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="min-w-0 space-y-6">
          <div className="min-w-0 overflow-hidden rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
            <h2 className="text-xl font-semibold">Upload JD</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              Upload JD dạng PDF hoặc TXT. Backend sẽ extract text và lưu vào nội dung JD để dùng cho matching.
            </p>
            <form onSubmit={handleJobDescriptionUpload} className="mt-6 space-y-4">
              <TextInput label="Tiêu đề vị trí" value={jdUploadTitle} onChange={setJdUploadTitle} placeholder="Backend Intern" />
              <TextInput label="Công ty" value={jdUploadCompany} onChange={setJdUploadCompany} placeholder="Tên công ty nếu có" />
              <input
                key={jdFileInputKey}
                type="file"
                accept="application/pdf,text/plain,.pdf,.txt"
                onChange={(event) => setSelectedJdFile(event.target.files?.[0] ?? null)}
                className="block w-full min-w-0 max-w-full rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200 file:mr-4 file:rounded-md file:border-0 file:bg-cyan-300 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-950"
              />
              <p className="text-xs leading-5 text-slate-500">Upload JD khi bạn có file từ nhà tuyển dụng. Nếu không, paste JD ở form bên dưới.</p>
              <button type="submit" disabled={!canUploadJd} className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70">
                {isUploadingJd ? "Đang đọc JD..." : "Upload JD"}
              </button>
            </form>
          </div>

          <div className="min-w-0 overflow-hidden rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
            <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <h2 className="text-xl font-semibold">{editingJobDescriptionId ? "Sửa JD" : "Paste JD"}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {editingJobDescriptionId ? "Cập nhật JD đã lưu. Các lần analysis mới sẽ dùng nội dung mới." : "Paste JD trực tiếp từ trang tuyển dụng nếu không có file."}
                </p>
              </div>
              {editingJobDescriptionId ? (
                <button type="button" onClick={resetJobDescriptionForm} className="w-full shrink-0 rounded-md border border-white/15 px-4 py-2 text-sm font-semibold transition hover:bg-white/10 sm:w-auto">
                  Hủy sửa
                </button>
              ) : null}
            </div>
            <form onSubmit={handleSaveJobDescription} className="mt-6 space-y-4">
              <TextInput label="Tiêu đề vị trí" value={jdTitle} onChange={setJdTitle} placeholder="Backend Intern" required />
              <TextInput label="Công ty" value={jdCompany} onChange={setJdCompany} placeholder="Tên công ty nếu có" />
              <TextInput label="Nguồn JD" value={jdSourceUrl} onChange={setJdSourceUrl} placeholder="https://..." />
              <label className="block text-sm font-medium text-slate-200">
                Nội dung JD
                <textarea required rows={8} value={jdContent} onChange={(event) => setJdContent(event.target.value)} placeholder="Paste mô tả công việc, yêu cầu kỹ năng, trách nhiệm..." className="mt-2 w-full min-w-0 resize-y rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300" />
              </label>
              <button type="submit" disabled={!canSaveJd} className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70">
                {isSavingJd ? "Đang lưu JD..." : editingJobDescriptionId ? "Lưu cập nhật" : "Lưu JD"}
              </button>
            </form>
          </div>
        </div>
      </section>

      <section className="mx-auto w-full min-w-0 max-w-6xl px-4 pb-10 sm:px-6">
        {error ? <p className="mb-4 rounded-md bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
        {statusMessage ? <p className="mb-4 rounded-md bg-emerald-500/10 p-3 text-sm text-emerald-200">{statusMessage}</p> : null}

        <div className="min-w-0 overflow-hidden rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">JD đã lưu</h2>
          <div className="mt-4 space-y-3">
            {jobDescriptions.length === 0 ? (
              <p className="text-sm leading-6 text-slate-400">Chưa có JD nào. Paste hoặc upload JD để hệ thống có dữ liệu matching.</p>
            ) : (
              jobDescriptions.map((job) => (
                <article key={job.id} className="min-w-0 overflow-hidden rounded-md border border-white/10 bg-slate-950/60 p-4">
                  <div className="flex min-w-0 flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0 flex-1">
                      <div className="flex min-w-0 flex-col gap-1 sm:flex-row sm:items-start sm:gap-3">
                        <h3 className="min-w-0 break-words font-medium leading-6 text-slate-100">{job.title}</h3>
                        {job.company ? <p className="break-words text-sm leading-6 text-cyan-200">{job.company}</p> : null}
                      </div>
                      {job.source_url ? <p title={job.source_url} className="mt-1 break-all text-xs leading-5 text-slate-500">{job.source_url}</p> : null}
                      <p className="mt-1 text-xs text-slate-500">Cập nhật: {new Date(job.updated_at).toLocaleString("vi-VN")}</p>
                    </div>
                    <div className="flex w-full shrink-0 flex-wrap gap-2 sm:w-auto">
                      <button type="button" onClick={() => startEditJobDescription(job)} className="flex-1 rounded-md border border-white/15 px-3 py-2 text-sm font-semibold transition hover:bg-white/10 sm:flex-none">
                        Sửa
                      </button>
                      <button type="button" onClick={() => void handleDeleteJobDescription(job)} disabled={deletingJobDescriptionId === job.id} className="flex-1 rounded-md border border-red-300/30 px-3 py-2 text-sm font-semibold text-red-200 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-60 sm:flex-none">
                        {deletingJobDescriptionId === job.id ? "Đang xóa..." : "Xóa"}
                      </button>
                    </div>
                  </div>
                  <p className="mt-3 line-clamp-4 break-words whitespace-pre-line text-sm leading-6 text-slate-300">{job.content}</p>
                </article>
              ))
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

function TextInput({ label, value, onChange, placeholder, required = false }: { label: string; value: string; onChange: (value: string) => void; placeholder: string; required?: boolean }) {
  return (
    <label className="block min-w-0 text-sm font-medium text-slate-200">
      {label}
      <input type="text" required={required} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className="mt-2 w-full min-w-0 rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300" />
    </label>
  );
}
