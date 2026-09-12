import React from "react";
import { TransportOptionData } from "../types/trip";
import { PlaneIcon } from "./Icons";

interface TransportCardProps {
  transport: {
    origin: string;
    destination: string;
    options: TransportOptionData[];
  };
}

export function TransportCard({ transport }: TransportCardProps) {
  const getModeLabel = (mode: string) => {
    switch (mode.toLowerCase()) {
      case "flight":
        return "✈️ Flight";
      case "train":
        return "🚆 Train";
      case "bus":
        return "🚌 Bus";
      default:
        return mode;
    }
  };

  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800 rounded-2xl p-5 space-y-4 shadow-sm">
      <div className="flex items-center gap-2 border-b border-neutral-100 dark:border-neutral-800 pb-3">
        <div className="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400">
          <PlaneIcon className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-bold text-base text-neutral-900 dark:text-white">
            Transport Options
          </h3>
          <p className="text-xs text-neutral-500 dark:text-neutral-400">
            {transport.origin} to {transport.destination}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {transport.options.map((opt, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-neutral-50/70 dark:bg-neutral-950/40 border border-neutral-200/60 dark:border-neutral-800/60 space-y-2 flex flex-col justify-between"
          >
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-neutral-900 dark:text-white">
                  {getModeLabel(opt.mode)}
                </span>
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 border border-blue-200/50 dark:border-blue-800/50">
                  {opt.recommendation_type}
                </span>
              </div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">
                Duration: {opt.duration} &bull; {opt.comfort_level} Comfort
              </p>
            </div>

            <div className="pt-2 border-t border-neutral-200/40 dark:border-neutral-800/40 flex justify-between items-center text-xs">
              <span className="text-neutral-500">Est. Total:</span>
              <span className="font-bold text-neutral-900 dark:text-white">
                ₹{opt.estimated_cost_min.toLocaleString()} – ₹
                {opt.estimated_cost_max.toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
