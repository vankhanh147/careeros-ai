"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import {
  createJobDescription,
  deleteJobDescription,
  deleteResume,
  getMyJobDescriptions,
  getMyResumes,
  getResumeAccessUrl,
  updateJobDescription,
  uploadJobDescription,
  uploadResume,
  type JobDescription,
  type Resume
} from "@/lib/api/documents";
import { getAnalysisHistory, type MatchAnalysis } from "@/lib/api/analysis";
import { useAuth } from "@/lib/auth/AuthContext";

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;

export default function DocumentsPage() {
  const router = useRouter();
  const { token, isAuthenticated, isLoading } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([]);
  const [analyses, setAnalyses] = useState<MatchAnalysis[]>([]);
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
  const [resumeAccessAction, setResumeAccessAction] = useState<{ resumeId: number; action: "view" | "download" } | null>(null);
  const [deletingJobDescriptionId, setDeletingJobDescriptionId] = useState<number | null>(null);
  const [viewingJobDescription, setViewingJobDescription] = useState<JobDescription | null>(null);
  const modalCloseButtonRef = useRef<HTMLButtonElement>(null);
  const canUploadResume = Boolean(selectedResumeFile) && !isUploadingResume;
  const canUploadJd = Boolean(selectedJdFile) && !isUploadingJd;
  const canSaveJd = jdTitle.trim().length > 0 && jdContent.trim().length > 0 && !isSavingJd;
  const latestAnalysisByResume = useMemo(() => {
    const byResume = new Map<number, MatchAnalysis>();
    for (const analysis of analyses) {
      if (!byResume.has(analysis.resume_id)) {
        byResume.set(analysis.resume_id, analysis);
      }
    }
    return byResume;
  }, [analyses]);

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
        const [resumeList, jdList, analysisHistory] = await Promise.all([
          getMyResumes(token),
          getMyJobDescriptions(token),
          getAnalysisHistory(token).catch(() => [])
        ]);
        if (isMounted) {
          setResumes(resumeList);
          setJobDescriptions(jdList);
          setAnalyses(analysisHistory);
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

  useEffect(() => {
    if (!viewingJobDescription) return;

    const previousOverflow = document.body.style.overflow;
    const previouslyFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setViewingJobDescription(null);
      }
    }

    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", handleKeyDown);
    window.requestAnimationFrame(() => modalCloseButtonRef.current?.focus());

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", handleKeyDown);
      previouslyFocused?.focus();
    };
  }, [viewingJobDescription]);

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
      setStatusMessage("Đã tải CV PDF lên.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tải CV lên.");
    } finally {
      setIsUploadingResume(false);
    }
  }

  async function handleResumeAccess(resume: Resume, action: "view" | "download") {
    if (!token) {
      router.replace("/login");
      return;
    }

    setError("");
    setStatusMessage("");
    setResumeAccessAction({ resumeId: resume.id, action });
    try {
      const access = await getResumeAccessUrl(token, resume.id);
      const openedWindow = window.open(access.access_url, "_blank");
      if (openedWindow) {
        openedWindow.opener = null;
      } else {
        setError("Trình duyệt đã chặn cửa sổ mới. Vui lòng cho phép mở tab và thử lại.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tạo liên kết xem CV. Vui lòng thử lại.");
    } finally {
      setResumeAccessAction(null);
    }
  }

  async function handleDeleteResume(resume: Resume) {
    if (!token) {
      router.replace("/login");
      return;
    }
    const confirmed = window.confirm(`Xóa CV "${resume.file_name}"? Tệp lưu trữ tương ứng cũng sẽ được xóa nếu còn tồn tại.`);
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
      setError("JD hiện hỗ trợ tệp PDF hoặc TXT.");
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
      setStatusMessage("Đã tải lên và đọc nội dung JD.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tải JD lên.");
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
    document.getElementById("job-description-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
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
      if (viewingJobDescription?.id === job.id) {
        setViewingJobDescription(null);
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
        <div id="resume-upload" className="min-w-0 overflow-hidden rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Tải CV PDF lên</h2>
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
              {isUploadingResume ? "Đang tải CV lên..." : "Tải CV lên"}
            </button>
          </form>

          <div className="mt-8">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">CV đã tải lên</h3>
              {resumes.length > 0 ? <span className="text-xs text-slate-500">{resumes.length} tài liệu</span> : null}
            </div>
            <div className="mt-4 space-y-3">
              {resumes.length === 0 ? (
                <DocumentEmptyState
                  title="Bạn chưa tải CV lên."
                  description="CareerOS AI sẽ dùng CV để phân tích mức độ phù hợp, phát hiện khoảng trống kỹ năng, tạo Roadmap và hỗ trợ luyện phỏng vấn."
                  href="#resume-upload"
                  cta="Tải CV lên"
                />
              ) : (
                resumes.map((resume) => {
                  const uploadedAt = formatDocumentDate(resume.created_at);
                  const fileSize = formatFileSize(getResumeFileSize(resume));
                  const latestAnalysis = latestAnalysisByResume.get(resume.id);
                  const extractionStatus = latestAnalysis
                    ? "Đã phân tích"
                    : resume.extracted_text?.trim()
                      ? "Đã trích xuất"
                      : "Đang chờ";

                  return (
                    <article key={resume.id} className="min-w-0 overflow-hidden rounded-md border border-white/10 bg-slate-950/60 p-4 transition hover:border-white/20">
                      <div className="flex min-w-0 flex-col gap-4">
                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2.5 py-1 text-xs font-semibold text-cyan-200">PDF</span>
                            <span className={`rounded-full border px-2.5 py-1 text-xs font-medium ${latestAnalysis ? "border-emerald-300/20 bg-emerald-300/10 text-emerald-200" : resume.extracted_text?.trim() ? "border-cyan-300/20 bg-cyan-300/10 text-cyan-200" : "border-white/10 bg-white/5 text-slate-300"}`}>
                              {extractionStatus}
                            </span>
                          </div>
                          <h4 className="mt-3 break-words text-sm font-semibold leading-6 text-slate-100">{resume.file_name}</h4>
                          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
                            <span>{uploadedAt ? `Tải lên: ${uploadedAt}` : "Chưa có ngày tải lên"}</span>
                            {fileSize ? <span>Dung lượng: {fileSize}</span> : null}
                          </div>
                        </div>

                        <ResumeIntelligenceCard resume={resume} analysis={latestAnalysis} />

                        <div className="flex w-full flex-wrap gap-2">
                          <button
                            type="button"
                            onClick={() => void handleResumeAccess(resume, "view")}
                            disabled={resumeAccessAction?.resumeId === resume.id}
                            className="flex-1 rounded-md border border-cyan-300/30 px-3 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-300/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60 disabled:cursor-wait disabled:opacity-60 sm:flex-none"
                          >
                            {resumeAccessAction?.resumeId === resume.id && resumeAccessAction.action === "view" ? "Đang mở..." : "Xem"}
                          </button>
                          <button
                            type="button"
                            onClick={() => void handleResumeAccess(resume, "download")}
                            disabled={resumeAccessAction?.resumeId === resume.id}
                            className="flex-1 rounded-md border border-white/15 px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60 disabled:cursor-wait disabled:opacity-60 sm:flex-none"
                          >
                            {resumeAccessAction?.resumeId === resume.id && resumeAccessAction.action === "download" ? "Đang chuẩn bị..." : "Tải xuống"}
                          </button>
                          <button type="button" onClick={() => void handleDeleteResume(resume)} disabled={deletingResumeId === resume.id || resumeAccessAction?.resumeId === resume.id} className="flex-1 rounded-md border border-red-300/30 px-3 py-2 text-sm font-semibold text-red-200 transition hover:bg-red-500/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-300/50 disabled:cursor-not-allowed disabled:opacity-60 sm:flex-none">
                            {deletingResumeId === resume.id ? "Đang xóa..." : "Xóa"}
                          </button>
                        </div>
                      </div>
                    </article>
                  );
                })
              )}
            </div>
          </div>
        </div>

        <div className="min-w-0 space-y-6">
          <div className="min-w-0 overflow-hidden rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
            <h2 className="text-xl font-semibold">Tải JD lên</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              Tải JD dạng PDF hoặc TXT. Hệ thống sẽ đọc nội dung để dùng cho Resume ↔ JD Matching.
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
              <p className="text-xs leading-5 text-slate-500">Tải JD lên khi bạn có tệp từ nhà tuyển dụng. Nếu không, hãy dán nội dung JD vào biểu mẫu bên dưới.</p>
              <button type="submit" disabled={!canUploadJd} className="rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70">
                {isUploadingJd ? "Đang đọc JD..." : "Tải JD lên"}
              </button>
            </form>
          </div>

          <div id="job-description-form" className="min-w-0 overflow-hidden rounded-lg border border-white/10 bg-white/5 p-5 sm:p-6">
            <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <h2 className="text-xl font-semibold">{editingJobDescriptionId ? "Sửa JD" : "Dán nội dung JD"}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {editingJobDescriptionId ? "Cập nhật JD đã lưu. Các lần analysis mới sẽ dùng nội dung mới." : "Dán JD trực tiếp từ trang tuyển dụng nếu bạn không có tệp."}
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
                <textarea required rows={8} value={jdContent} onChange={(event) => setJdContent(event.target.value)} placeholder="Dán mô tả công việc, yêu cầu kỹ năng và trách nhiệm..." className="mt-2 w-full min-w-0 resize-y rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300" />
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
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-xl font-semibold">JD đã lưu</h2>
            {jobDescriptions.length > 0 ? <span className="text-xs text-slate-500">{jobDescriptions.length} vị trí</span> : null}
          </div>
          <div className="mt-4 space-y-3">
            {jobDescriptions.length === 0 ? (
              <DocumentEmptyState
                title="Bạn chưa lưu Job Description."
                description="Thêm JD để CareerOS AI so khớp hồ sơ của bạn với vị trí mục tiêu."
                href="#job-description-form"
                cta="Thêm JD"
              />
            ) : (
              jobDescriptions.map((job) => {
                const createdAt = formatDocumentDate(job.created_at);
                const updatedAt = formatDocumentDate(job.updated_at);

                return (
                  <article key={job.id} className="min-w-0 overflow-hidden rounded-md border border-white/10 bg-slate-950/60 p-4 transition hover:border-white/20">
                    <div className="flex min-w-0 flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2.5 py-1 text-xs font-semibold text-cyan-200">JD</span>
                          <span className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-2.5 py-1 text-xs font-medium text-emerald-200">Nội dung đã sẵn sàng</span>
                          <span className="break-words text-xs text-slate-400">{job.company?.trim() || "Chưa có công ty"}</span>
                        </div>
                        <h3 className="mt-3 min-w-0 break-words font-semibold leading-6 text-slate-100">{job.title}</h3>
                        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
                          {createdAt ? <span>Tạo: {createdAt}</span> : null}
                          {updatedAt ? <span>Cập nhật: {updatedAt}</span> : null}
                        </div>
                        {job.source_url ? <p title={job.source_url} className="mt-2 truncate text-xs leading-5 text-slate-500">{job.source_url}</p> : null}
                        <p className="mt-3 line-clamp-3 break-words whitespace-pre-line text-sm leading-6 text-slate-300">{job.content}</p>
                      </div>

                      <div className="flex w-full shrink-0 flex-wrap gap-2 lg:w-auto">
                        <button type="button" onClick={() => setViewingJobDescription(job)} className="flex-1 rounded-md border border-cyan-300/30 px-3 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-300/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60 sm:flex-none">
                          Xem
                        </button>
                        <button type="button" onClick={() => startEditJobDescription(job)} className="flex-1 rounded-md border border-white/15 px-3 py-2 text-sm font-semibold transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60 sm:flex-none">
                          Sửa
                        </button>
                        <button type="button" onClick={() => void handleDeleteJobDescription(job)} disabled={deletingJobDescriptionId === job.id} className="flex-1 rounded-md border border-red-300/30 px-3 py-2 text-sm font-semibold text-red-200 transition hover:bg-red-500/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-300/50 disabled:cursor-not-allowed disabled:opacity-60 sm:flex-none">
                          {deletingJobDescriptionId === job.id ? "Đang xóa..." : "Xóa"}
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })
            )}
          </div>
        </div>
      </section>

      {viewingJobDescription ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 p-4 backdrop-blur-sm"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setViewingJobDescription(null);
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="jd-preview-title"
            aria-describedby="jd-preview-content"
            className="max-h-[85vh] w-full max-w-3xl overflow-y-auto rounded-lg border border-white/15 bg-slate-900 p-5 shadow-2xl sm:p-6"
          >
            <div className="flex items-start justify-between gap-4 border-b border-white/10 pb-4">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2.5 py-1 text-xs font-semibold text-cyan-200">JD</span>
                  <span className="break-words text-sm text-slate-400">{viewingJobDescription.company?.trim() || "Chưa có công ty"}</span>
                </div>
                <h2 id="jd-preview-title" className="mt-3 break-words text-xl font-semibold text-slate-100">{viewingJobDescription.title}</h2>
                <p className="mt-2 text-xs text-slate-500">
                  {formatDocumentDate(viewingJobDescription.created_at) ? `Tạo: ${formatDocumentDate(viewingJobDescription.created_at)}` : "Chưa có ngày tạo"}
                </p>
              </div>
              <button
                ref={modalCloseButtonRef}
                type="button"
                onClick={() => setViewingJobDescription(null)}
                aria-label="Đóng cửa sổ xem JD"
                className="shrink-0 rounded-md border border-white/15 px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60"
              >
                Đóng
              </button>
            </div>

            {viewingJobDescription.source_url ? (
              <p className="mt-4 break-all text-xs leading-5 text-slate-500">{viewingJobDescription.source_url}</p>
            ) : null}
            <div id="jd-preview-content" className="mt-5 whitespace-pre-wrap break-words text-sm leading-7 text-slate-200">
              {viewingJobDescription.content}
            </div>

            <div className="mt-6 flex justify-end border-t border-white/10 pt-4">
              <button type="button" onClick={() => setViewingJobDescription(null)} className="w-full rounded-md bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-200 sm:w-auto">
                Đóng
              </button>
            </div>
          </section>
        </div>
      ) : null}
    </main>
  );
}

function ResumeIntelligenceCard({ resume, analysis }: { resume: Resume; analysis?: MatchAnalysis }) {
  const detectedSkills = Array.from(new Set((analysis?.resume_detected_skills ?? []).filter((skill) => skill.trim())));
  const visibleSkills = detectedSkills.slice(0, 8);
  const remainingSkillCount = Math.max(0, detectedSkills.length - visibleSkills.length);
  const roleFamily = analysis?.scoring_breakdown.resume_role_family?.trim();
  const stackGroups = (analysis?.scoring_breakdown.resume_stack_groups ?? []).filter((stack) => stack.trim());
  const extractedPreview = analysis?.resume_text_preview?.trim() || resume.extracted_text?.trim() || "";
  const hasAnalysis = Boolean(analysis);
  const hasSnapshot = Boolean(roleFamily || stackGroups.length);

  return (
    <section className="rounded-md border border-cyan-300/15 bg-cyan-300/5 p-4" aria-label={`Tóm tắt AI cho ${resume.file_name}`}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-cyan-300">Tóm tắt tài liệu bằng AI</p>
          <h5 className="mt-2 text-sm font-semibold text-slate-100">AI đã đọc gì từ CV?</h5>
        </div>
        <span className={`w-fit shrink-0 rounded-full border px-2.5 py-1 text-xs font-medium ${hasAnalysis ? "border-emerald-300/20 bg-emerald-300/10 text-emerald-200" : extractedPreview ? "border-cyan-300/20 bg-cyan-300/10 text-cyan-200" : "border-white/10 bg-white/5 text-slate-400"}`}>
          {hasAnalysis ? "Đã phân tích" : extractedPreview ? "Đã trích xuất" : "Đang chờ phân tích"}
        </span>
      </div>

      {hasAnalysis ? (
        <>
          <div className="mt-4 border-t border-white/10 pt-4">
            <div className="flex items-center justify-between gap-3">
              <h6 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Kỹ năng phát hiện</h6>
              <span className="text-xs text-slate-500">{detectedSkills.length} kỹ năng</span>
            </div>
            {visibleSkills.length > 0 ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {visibleSkills.map((skill) => (
                  <span key={skill} className="max-w-full break-words rounded-full border border-white/10 bg-slate-950/60 px-3 py-1 text-xs text-slate-200">
                    {skill}
                  </span>
                ))}
                {remainingSkillCount > 0 ? (
                  <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs font-medium text-cyan-200">
                    +{remainingSkillCount} kỹ năng khác
                  </span>
                ) : null}
              </div>
            ) : (
              <p className="mt-3 text-sm leading-6 text-slate-400">Chưa phát hiện kỹ năng rõ ràng trong lần phân tích gần nhất.</p>
            )}
          </div>

          {hasSnapshot ? (
            <div className="mt-4 border-t border-white/10 pt-4">
              <h6 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Tóm tắt nghề nghiệp</h6>
              <dl className="mt-3 grid gap-3 sm:grid-cols-2">
                {roleFamily ? (
                  <div className="min-w-0 rounded-md bg-slate-950/50 p-3">
                    <dt className="text-xs text-slate-500">Nhóm vai trò phát hiện</dt>
                    <dd className="mt-1 break-words text-sm font-medium text-slate-200">{formatRoleFamily(roleFamily)}</dd>
                  </div>
                ) : null}
                {stackGroups.length > 0 ? (
                  <div className="min-w-0 rounded-md bg-slate-950/50 p-3">
                    <dt className="text-xs text-slate-500">Stack phát hiện</dt>
                    <dd className="mt-1 break-words text-sm font-medium text-slate-200">{stackGroups.join(", ")}</dd>
                  </div>
                ) : null}
              </dl>
            </div>
          ) : null}

          {extractedPreview ? (
            <div className="mt-4 border-t border-white/10 pt-4">
              <h6 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Nội dung AI đã đọc</h6>
              <p className="mt-2 line-clamp-3 whitespace-pre-line break-words text-sm leading-6 text-slate-400">{extractedPreview}</p>
            </div>
          ) : null}

          <ReadyFeatures />
        </>
      ) : (
        <div className="mt-4 border-t border-white/10 pt-4">
          {extractedPreview ? (
            <>
              <p className="text-sm leading-6 text-slate-300">Nội dung CV đã được trích xuất. Kỹ năng và tóm tắt nghề nghiệp sẽ xuất hiện sau lần matching đầu tiên.</p>
              <p className="mt-3 line-clamp-3 whitespace-pre-line break-words text-sm leading-6 text-slate-500">{extractedPreview}</p>
            </>
          ) : (
            <p className="text-sm leading-6 text-slate-400">AI sẽ hiển thị tóm tắt sau khi tài liệu được phân tích cùng một JD.</p>
          )}
          <div className="mt-4 rounded-md border border-white/10 bg-slate-950/50 p-3">
            <p className="text-sm font-medium text-slate-200">Bước tiếp theo</p>
            <p className="mt-1 text-xs leading-5 text-slate-500">Chọn CV này và một JD để chạy Resume ↔ JD Matching.</p>
            <Link href="/analysis" className="mt-3 inline-flex rounded-md border border-cyan-300/30 px-3 py-2 text-xs font-semibold text-cyan-100 transition hover:bg-cyan-300/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60">
              Đi tới phân tích
            </Link>
          </div>
        </div>
      )}
    </section>
  );
}

function ReadyFeatures() {
  const features = ["Resume Matching", "Skill Gap", "Roadmap", "Mock Interview"];
  return (
    <div className="mt-4 border-t border-white/10 pt-4">
      <h6 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">AI đã sẵn sàng cho</h6>
      <ul className="mt-3 grid gap-2 sm:grid-cols-2">
        {features.map((feature) => (
          <li key={feature} className="flex items-center gap-2 text-sm text-slate-300">
            <span aria-hidden="true" className="text-emerald-300">✓</span>
            {feature}
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatRoleFamily(value: string): string {
  const labels: Record<string, string> = {
    backend: "Backend Developer",
    frontend: "Frontend Developer",
    fullstack: "Fullstack Developer",
    "ai/data": "AI / Data",
    mobile: "Mobile Developer",
    devops: "DevOps",
    cybersecurity: "Cybersecurity",
    "qa/testing": "QA / Testing",
    "general software": "Phát triển phần mềm"
  };
  return labels[value.toLowerCase()] ?? value;
}

function DocumentEmptyState({ title, description, href, cta }: { title: string; description: string; href: string; cta: string }) {
  return (
    <div className="rounded-md border border-dashed border-white/15 bg-slate-950/40 p-5">
      <h4 className="font-semibold text-slate-100">{title}</h4>
      <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>
      <a href={href} className="mt-4 inline-flex rounded-md border border-cyan-300/30 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-300/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60">
        {cta}
      </a>
    </div>
  );
}

function getResumeFileSize(resume: Resume): number | null {
  const size = resume.file_size ?? resume.size;
  return typeof size === "number" && Number.isFinite(size) && size >= 0 ? size : null;
}

function formatFileSize(bytes: number | null): string | null {
  if (bytes === null) return null;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDocumentDate(value: string | null | undefined): string | null {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toLocaleString("vi-VN");
}

function TextInput({ label, value, onChange, placeholder, required = false }: { label: string; value: string; onChange: (value: string) => void; placeholder: string; required?: boolean }) {
  return (
    <label className="block min-w-0 text-sm font-medium text-slate-200">
      {label}
      <input type="text" required={required} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className="mt-2 w-full min-w-0 rounded-md border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300" />
    </label>
  );
}
