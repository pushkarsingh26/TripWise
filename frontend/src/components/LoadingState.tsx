import React from "react";
import { SparklesIcon } from "./Icons";

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = "Tripwise is planning your trip..." }: LoadingStateProps) {
  return (
    <div className="flex items-start gap-3 p-4 rounded-2xl bg-indigo-50/40 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/50 max-w-xl animate-pulse">
      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shrink-0 shadow-sm">
        <SparklesIcon className="w-4 h-4 animate-spin" />
      </div>
      <div className="space-y-2 py-1">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
            Tripwise AI
          </span>
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-ping" />
        </div>
        <p className="text-sm font-medium text-neutral-800 dark:text-neutral-200">
          {message}
        </p>
      </div>
    </div>
  );
}

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
