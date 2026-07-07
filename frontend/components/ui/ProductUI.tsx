import Link from "next/link";
import type { ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type BadgeTone = "success" | "info" | "warning" | "neutral";
type AlertTone = "success" | "error" | "warning" | "info";

const BUTTON_VARIANTS: Record<ButtonVariant, string> = {
  primary: "bg-cyan-300 text-slate-950 hover:bg-cyan-200",
  secondary: "border border-white/15 text-slate-100 hover:bg-white/10",
  danger: "border border-red-300/25 text-red-200 hover:bg-red-300/10",
  ghost: "text-cyan-100 hover:bg-cyan-300/10"
};

const BADGE_TONES: Record<BadgeTone, string> = {
  success: "border-emerald-300/20 bg-emerald-300/10 text-emerald-100",
  info: "border-cyan-300/20 bg-cyan-300/10 text-cyan-100",
  warning: "border-amber-300/20 bg-amber-300/10 text-amber-100",
  neutral: "border-white/10 bg-white/5 text-slate-400"
};

const ALERT_TONES: Record<AlertTone, string> = {
  success: "border-emerald-300/20 bg-emerald-300/10 text-emerald-100",
  error: "border-red-300/20 bg-red-500/10 text-red-100",
  warning: "border-amber-300/20 bg-amber-300/10 text-amber-100",
  info: "border-cyan-300/20 bg-cyan-300/10 text-cyan-100"
};

const ALERT_LABELS: Record<AlertTone, string> = {
  success: "Đã xong",
  error: "Cần kiểm tra",
  warning: "Lưu ý",
  info: "Thông tin"
};

export function buttonStyles(variant: ButtonVariant = "secondary", className = "") {
  return [
    "inline-flex min-h-10 items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition",
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300",
    "disabled:cursor-not-allowed disabled:opacity-60",
    BUTTON_VARIANTS[variant],
    className
  ].filter(Boolean).join(" ");
}

export function StatusBadge({ children, tone = "neutral", className = "" }: { children: ReactNode; tone?: BadgeTone; className?: string }) {
  return (
    <span className={`inline-flex min-h-7 max-w-full items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${BADGE_TONES[tone]} ${className}`}>
      <span className="break-words">{children}</span>
    </span>
  );
}

export function InlineAlert({ tone = "info", children, className = "" }: { tone?: AlertTone; children: ReactNode; className?: string }) {
  const isError = tone === "error";
  return (
    <div role={isError ? "alert" : "status"} aria-live={isError ? "assertive" : "polite"} className={`rounded-md border p-3 text-sm leading-6 ${ALERT_TONES[tone]} ${className}`}>
      <span className="font-semibold">{ALERT_LABELS[tone]}: </span>
      <span className="break-words">{children}</span>
    </div>
  );
}

export function PageLoading({ title, description }: { title: string; description?: string }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white sm:px-6" aria-busy="true">
      <section className="w-full max-w-md rounded-lg border border-white/10 bg-white/5 p-6">
        <div className="animate-pulse" aria-hidden="true">
          <div className="h-5 w-2/3 rounded bg-white/10" />
          <div className="mt-3 h-3 w-full rounded bg-white/10" />
          <div className="mt-2 h-3 w-4/5 rounded bg-white/10" />
        </div>
        <p className="sr-only">{title}{description ? ` ${description}` : ""}</p>
      </section>
    </main>
  );
}

export function EmptyState({
  title,
  description,
  action
}: {
  title: string;
  description: string;
  action?: { href: string; label: string };
}) {
  return (
    <section className="rounded-lg border border-white/10 bg-white/5 p-6 text-center">
      <span aria-hidden="true" className="mx-auto flex h-10 w-10 items-center justify-center rounded-full border border-cyan-300/20 bg-cyan-300/10 text-cyan-200">+</span>
      <h2 className="mt-4 text-lg font-semibold text-slate-100">{title}</h2>
      <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-400">{description}</p>
      {action ? <Link href={action.href} className={buttonStyles("secondary", "mt-5")}>{action.label}</Link> : null}
    </section>
  );
}
