import React from "react";
import { PlusIcon, SparklesIcon } from "./Icons";

interface HeaderProps {
  backendStatus: string;
  onNewTrip: () => void;
  hasActiveTrip: boolean;
}

export function Header({ backendStatus, onNewTrip, hasActiveTrip }: HeaderProps) {
  const isConnected = backendStatus === "Connected";

  return (
    <header className="sticky top-0 z-30 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-md border-b border-neutral-200 dark:border-neutral-800 transition-colors">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-purple-600 flex items-center justify-center text-white shadow-sm shadow-indigo-500/20">
            <SparklesIcon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg text-neutral-900 dark:text-white tracking-tight leading-none">
                Tripwise
              </h1>
              <span className="text-[10px] font-medium uppercase tracking-wider px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200/50 dark:border-indigo-800/50">
                AI Planner
              </span>
            </div>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 font-normal">
              Conversational Travel Intelligence
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-neutral-100 dark:bg-neutral-800 border border-neutral-200/60 dark:border-neutral-700/60 text-neutral-600 dark:text-neutral-300"
            title={`Backend Status: ${backendStatus}`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
              }`}
            />
            <span className="hidden sm:inline">{isConnected ? "Connected" : "Offline"}</span>
          </div>

          {hasActiveTrip && (
            <button
              onClick={onNewTrip}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-neutral-700 dark:text-neutral-200 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-800 dark:hover:bg-neutral-700 rounded-lg transition-colors border border-neutral-200 dark:border-neutral-700 active:scale-95"
            >
              <PlusIcon className="w-3.5 h-3.5" />
              <span>New Trip</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
