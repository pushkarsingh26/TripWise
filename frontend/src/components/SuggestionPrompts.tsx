import React from "react";
import { SparklesIcon } from "./Icons";

interface SuggestionPromptsProps {
  onSelectPrompt: (promptText: string) => void;
}

export function SuggestionPrompts({ onSelectPrompt }: SuggestionPromptsProps) {
  const suggestions = [
    {
      title: "5-Day Goa Beach Trip",
      prompt: "Plan a 5-day trip from Indore to Goa for 2 people with a budget of ₹30,000. I love beaches and food.",
      lang: "English",
      badge: "Popular",
    },
    {
      title: "हिंदी में ट्रिप प्लान करें",
      prompt: "मुझे इंदौर से गोवा का 5 दिन का ट्रिप प्लान करना है, 2 लोगों के लिए बजट ₹30,000 है।",
      lang: "Hindi",
      badge: "हिन्दी",
    },
    {
      title: "Hinglish Budget Plan",
      prompt: "Indore se Goa 5 din ka trip plan karo 2 logon ke liye, budget 30000 hai.",
      lang: "Hinglish",
      badge: "Hinglish",
    },
  ];

  return (
    <div className="py-12 px-4 max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200/60 dark:border-indigo-800/60 text-indigo-600 dark:text-indigo-400 text-xs font-medium">
          <SparklesIcon className="w-3.5 h-3.5" />
          <span>Plan smarter. Travel better.</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-neutral-900 dark:text-white tracking-tight">
          Where to next?
        </h2>
        <p className="text-sm sm:text-base text-neutral-600 dark:text-neutral-400 max-w-lg mx-auto leading-relaxed">
          Describe your trip naturally in English, Hindi, or Hinglish. Tripwise will optimize transport, stay, budget, and day-by-day itineraries.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {suggestions.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(item.prompt)}
            className="group text-left p-4 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800 hover:border-indigo-400 dark:hover:border-indigo-600 hover:shadow-md hover:shadow-indigo-500/5 transition-all flex flex-col justify-between space-y-3"
          >
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-neutral-400 dark:text-neutral-500 uppercase tracking-wider">
                  {item.lang}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 font-medium">
                  {item.badge}
                </span>
              </div>
              <h3 className="font-semibold text-sm text-neutral-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                {item.title}
              </h3>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 line-clamp-2 leading-relaxed">
                &ldquo;{item.prompt}&rdquo;
              </p>
            </div>
            <div className="text-xs font-medium text-indigo-600 dark:text-indigo-400 flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
              <span>Try this prompt</span>
              <span>&rarr;</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
