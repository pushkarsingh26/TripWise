import React from "react";
import { ItineraryResultData } from "../types/trip";
import { CalendarIcon, ClockIcon } from "./Icons";

interface ItineraryTimelineProps {
  itinerary: ItineraryResultData;
}

export function ItineraryTimeline({ itinerary }: ItineraryTimelineProps) {
  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800 rounded-2xl p-5 space-y-5 shadow-sm">
      <div className="flex items-center justify-between border-b border-neutral-100 dark:border-neutral-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-violet-50 dark:bg-violet-950 text-violet-600 dark:text-violet-400">
            <CalendarIcon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-neutral-900 dark:text-white">
              Day-by-Day Itinerary
            </h3>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              {itinerary.destination} &bull; {itinerary.duration_days} Days Scheduled
            </p>
          </div>
        </div>

        {itinerary.is_estimate && (
          <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 font-medium">
            Illustrative Estimate
          </span>
        )}
      </div>

      <div className="space-y-6">
        {itinerary.days.map((day) => (
          <div key={day.day_number} className="space-y-3">
            <div className="flex items-center justify-between bg-neutral-50 dark:bg-neutral-950/80 px-3.5 py-2 rounded-xl border border-neutral-200/60 dark:border-neutral-800/60 text-xs font-semibold">
              <span className="text-neutral-900 dark:text-white flex items-center gap-2">
                <span className="w-6 h-6 rounded-lg bg-indigo-600 text-white flex items-center justify-center text-[11px] font-bold">
                  D{day.day_number}
                </span>
                <span>{day.title}</span>
                <span className="text-neutral-400 font-normal">({day.date})</span>
              </span>
              <span className="text-neutral-500 dark:text-neutral-400 font-normal">
                Est. Day Cost: ₹{day.estimated_day_cost_min.toLocaleString()} – ₹
                {day.estimated_day_cost_max.toLocaleString()}
              </span>
            </div>

            {day.activities.length === 0 ? (
              <p className="text-xs text-neutral-400 italic pl-4">
                Free exploration & relaxation day
              </p>
            ) : (
              <div className="relative pl-6 space-y-3 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-neutral-200 dark:before:bg-neutral-800">
                {day.activities.map((act, idx) => (
                  <div key={idx} className="relative group">
                    <div className="absolute -left-6 top-3 w-2.5 h-2.5 rounded-full bg-indigo-600 ring-4 ring-white dark:ring-neutral-900" />
                    <div className="p-3.5 rounded-xl bg-neutral-50/70 dark:bg-neutral-950/40 border border-neutral-200/60 dark:border-neutral-800/60 space-y-1.5 hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors">
                      <div className="flex flex-wrap items-center justify-between gap-1.5">
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-neutral-900 dark:bg-neutral-800 text-white text-[11px] font-mono font-medium">
                            <ClockIcon className="w-3 h-3 text-indigo-400" />
                            {act.start_time} – {act.end_time}
                          </span>
                          <span className="font-semibold text-sm text-neutral-900 dark:text-white">
                            {act.name}
                          </span>
                        </div>
                        <span className="text-[10px] px-2 py-0.5 rounded bg-neutral-200/80 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 font-medium capitalize">
                          {act.category}
                        </span>
                      </div>

                      <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed">
                        {act.description}
                      </p>

                      <div className="flex justify-between items-center text-[11px] text-neutral-500 dark:text-neutral-400 pt-1 border-t border-neutral-200/40 dark:border-neutral-800/40">
                        <span>Duration: {act.duration}</span>
                        <span className="font-medium text-neutral-700 dark:text-neutral-300">
                          Est. Cost: ₹{act.estimated_cost_min.toLocaleString()} – ₹
                          {act.estimated_cost_max.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
