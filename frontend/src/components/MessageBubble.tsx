import React from "react";
import { ChatMessage } from "../types/trip";
import { SparklesIcon } from "./Icons";
import { TripOverviewCard } from "./TripOverviewCard";
import { BudgetSummary } from "./BudgetSummary";
import { ItineraryTimeline } from "./ItineraryTimeline";
import { TransportCard } from "./TransportCard";
import { AccommodationCard } from "./AccommodationCard";
import { ErrorState } from "./ErrorState";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === "user";
  const { plan, modificationResult, isError, missing } = message;

  if (isUser) {
    return (
      <div className="flex justify-end mb-4 animate-fade-in">
        <div className="max-w-xl bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 px-4 py-3 rounded-2xl rounded-tr-sm shadow-sm space-y-1">
          <div className="text-xs font-semibold opacity-60 text-right">You</div>
          <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
          <div className="text-[10px] opacity-40 text-right">{message.timestamp}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 mb-6 animate-fade-in">
      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-purple-600 flex items-center justify-center text-white shrink-0 shadow-sm mt-1">
        <SparklesIcon className="w-4 h-4" />
      </div>

      <div className="flex-1 space-y-4 max-w-3xl min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-neutral-900 dark:text-white">
            Tripwise AI
          </span>
          <span className="text-[10px] text-neutral-400 dark:text-neutral-500 font-mono">
            {message.timestamp}
          </span>
        </div>

        {/* Text Message Content */}
        {message.content && (
          <div className="p-4 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800 text-sm text-neutral-800 dark:text-neutral-200 leading-relaxed shadow-sm">
            {message.content}
          </div>
        )}

        {/* Missing Information Alert */}
        {missing && missing.length > 0 && (
          <div className="p-4 border border-amber-300 dark:border-amber-800/80 bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 text-xs rounded-2xl space-y-2">
            <p className="font-semibold text-sm">A little more details needed</p>
            <p>Please specify the following missing parameters to proceed:</p>
            <ul className="list-disc list-inside font-mono text-[11px] space-y-0.5">
              {missing.map((field) => (
                <li key={field}>{field}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Modification Result Alert */}
        {modificationResult && (
          <div
            className={`p-3.5 text-xs rounded-xl border ${
              modificationResult.status === "error"
                ? "bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-200"
                : modificationResult.status === "needs_clarification"
                ? "bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-950/40 dark:border-amber-800 dark:text-amber-200"
                : "bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-950/40 dark:border-emerald-800 dark:text-emerald-200"
            }`}
          >
            <p className="font-semibold text-sm">{modificationResult.message}</p>
          </div>
        )}

        {/* Error Alert */}
        {isError && <ErrorState message={message.content} />}

        {/* Full Plan Presentation */}
        {plan && plan.status === "success" && (
          <div className="space-y-4 pt-1">
            {/* 1. Trip Overview */}
            {plan.trip && (
              <TripOverviewCard
                trip={plan.trip}
                durationDays={plan.duration_days}
                durationNights={plan.duration_nights}
              />
            )}

            {/* 2. Budget Breakdown & Optimization */}
            {plan.budget && <BudgetSummary budget={plan.budget} />}

            {/* 3. Transport Options */}
            {plan.transport && <TransportCard transport={plan.transport} />}

            {/* 4. Accommodation Options */}
            {plan.accommodation && <AccommodationCard accommodation={plan.accommodation} />}

            {/* 5. Day-by-Day Itinerary */}
            {plan.itinerary && <ItineraryTimeline itinerary={plan.itinerary} />}
          </div>
        )}
      </div>
    </div>
  );
}
