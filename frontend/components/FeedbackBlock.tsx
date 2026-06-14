"use client";

import { useState } from "react";

import { submitFeedback, type FeedbackType } from "@/lib/api/feedback";

type FeedbackBlockProps = {
  token: string | null;
  feedbackType: FeedbackType;
};

export function FeedbackBlock({ token, feedbackType }: FeedbackBlockProps) {
  const [comment, setComment] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  async function handleSubmit(useful: boolean) {
    if (hasSubmitted) {
      return;
    }
    if (!token) {
      setError("Bạn cần đăng nhập để gửi góp ý.");
      return;
    }

    setError("");
    setStatus("");
    setIsSubmitting(true);

    try {
      await submitFeedback(token, {
        feedback_type: feedbackType,
        useful,
        comment: comment.trim() || undefined
      });
      setComment("");
      setHasSubmitted(true);
      setStatus("Cảm ơn bạn, góp ý đã được ghi nhận.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể gửi góp ý. Vui lòng thử lại.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="mt-5 rounded-lg border border-white/10 bg-white/5 p-4">
      <p className="text-sm font-semibold text-slate-100">Phần này có hữu ích không?</p>
      <p className="mt-1 text-xs leading-5 text-slate-400">Góp ý của bạn giúp CareerOS AI ưu tiên cải thiện đúng chỗ trong beta.</p>
      <div className="mt-3 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => void handleSubmit(true)}
          disabled={isSubmitting || hasSubmitted}
          className="rounded-md border border-emerald-300/30 bg-emerald-300/10 px-4 py-2 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-300/20 disabled:cursor-not-allowed disabled:opacity-60"
        >
          👍 Hữu ích
        </button>
        <button
          type="button"
          onClick={() => void handleSubmit(false)}
          disabled={isSubmitting || hasSubmitted}
          className="rounded-md border border-amber-300/30 bg-amber-300/10 px-4 py-2 text-sm font-semibold text-amber-100 transition hover:bg-amber-300/20 disabled:cursor-not-allowed disabled:opacity-60"
        >
          👎 Chưa hữu ích
        </button>
      </div>
      <label className="mt-4 block text-sm font-medium text-slate-300">
        Góp ý thêm
        <textarea
          rows={3}
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          disabled={isSubmitting || hasSubmitted}
          placeholder="Điểm nào cần rõ hơn hoặc hữu ích hơn?"
          className="mt-2 w-full resize-y rounded-md border border-white/10 bg-slate-950/60 px-3 py-2 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300"
        />
      </label>
      {status ? <p className="mt-3 text-sm text-emerald-200">{status}</p> : null}
      {error ? <p className="mt-3 text-sm text-red-200">{error}</p> : null}
    </section>
  );
}
