import React, { useRef, useEffect } from "react";
import { SendIcon, SparklesIcon } from "./Icons";

interface ComposerProps {
  inputMessage: string;
  setInputMessage: (msg: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  hasActiveTrip: boolean;
}

export function Composer({
  inputMessage,
  setInputMessage,
  onSubmit,
  isLoading,
  hasActiveTrip,
}: ComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [inputMessage]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (inputMessage.trim() && !isLoading) {
        onSubmit(e);
      }
    }
  };

  return (
    <div className="sticky bottom-0 z-20 bg-gradient-to-t from-white via-white/95 to-transparent dark:from-neutral-950 dark:via-neutral-950/95 dark:to-transparent pt-4 pb-6 px-4">
      <div className="max-w-3xl mx-auto">
        <form
          onSubmit={onSubmit}
          className="relative flex items-end gap-2 bg-neutral-50 dark:bg-neutral-900/90 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-2 shadow-lg shadow-neutral-900/5 focus-within:border-indigo-500/80 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all"
        >
          <div className="flex-1 pl-2 py-1">
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              placeholder={
                hasActiveTrip
                  ? "Modify your trip (e.g. 'Make it cheaper', 'Trip ka budget 25000 kar do', 'Remove expensive activities')..."
                  : "Describe your trip (e.g. 'Plan a 5-day Goa trip from Indore under ₹30,000 for 2 people')..."
              }
              className="w-full resize-none bg-transparent text-sm text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 focus:outline-none max-h-40 min-h-[24px] leading-relaxed"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className="flex items-center justify-center w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-40 disabled:hover:bg-indigo-600 transition-all shrink-0 active:scale-95 shadow-sm shadow-indigo-600/30"
            title="Send prompt"
          >
            {isLoading ? (
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <SendIcon className="w-4 h-4" />
            )}
          </button>
        </form>

        <div className="flex items-center justify-between px-3 mt-2 text-[11px] text-neutral-400 dark:text-neutral-500">
          <div className="flex items-center gap-1.5">
            <SparklesIcon className="w-3 h-3 text-indigo-500" />
            <span>Powered by Tripwise AI</span>
          </div>
          <span className="hidden sm:inline">Press Enter to send, Shift+Enter for newline</span>
        </div>
      </div>
    </div>
  );
}
