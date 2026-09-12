import React from "react";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200/80 dark:border-rose-900/80 text-rose-900 dark:text-rose-200 text-xs space-y-2 max-w-2xl">
      <div className="flex items-center justify-between">
        <span className="font-bold uppercase tracking-wider text-[11px] text-rose-600 dark:text-rose-400">
          Request Alert
        </span>
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-[11px] underline font-semibold text-rose-700 dark:text-rose-300 hover:text-rose-900"
          >
            Retry
          </button>
        )}
      </div>
      <p className="text-sm leading-relaxed">{message}</p>
    </div>
  );
}
