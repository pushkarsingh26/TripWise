import React from "react";
import { AccommodationOptionData } from "../types/trip";
import { HotelIcon } from "./Icons";

interface AccommodationCardProps {
  accommodation: {
    destination: string;
    nights: number;
    options: AccommodationOptionData[];
  };
}

export function AccommodationCard({ accommodation }: AccommodationCardProps) {
  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800 rounded-2xl p-5 space-y-4 shadow-sm">
      <div className="flex items-center gap-2 border-b border-neutral-100 dark:border-neutral-800 pb-3">
        <div className="p-1.5 rounded-lg bg-teal-50 dark:bg-teal-950 text-teal-600 dark:text-teal-400">
          <HotelIcon className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-bold text-base text-neutral-900 dark:text-white">
            Accommodation Options
          </h3>
          <p className="text-xs text-neutral-500 dark:text-neutral-400">
            {accommodation.destination} &bull; {accommodation.nights} Nights Stay
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {accommodation.options.map((acc, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-neutral-50/70 dark:bg-neutral-950/40 border border-neutral-200/60 dark:border-neutral-800/60 space-y-2 flex flex-col justify-between"
          >
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-neutral-900 dark:text-white">
                  {acc.name}
                </span>
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-teal-50 dark:bg-teal-950 text-teal-600 dark:text-teal-400 border border-teal-200/50 dark:border-teal-800/50">
                  {acc.category}
                </span>
              </div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 line-clamp-2">
                {acc.location_description}
              </p>
              <div className="text-[11px] text-neutral-500 pt-1">
                Est. Nightly: ₹{acc.estimated_price_per_night_min.toLocaleString()} – ₹
                {acc.estimated_price_per_night_max.toLocaleString()}
              </div>
            </div>

            <div className="pt-2 border-t border-neutral-200/40 dark:border-neutral-800/40 flex justify-between items-center text-xs">
              <span className="text-neutral-500">Total ({accommodation.nights} nights):</span>
              <span className="font-bold text-neutral-900 dark:text-white">
                ₹{acc.estimated_total_min.toLocaleString()} – ₹
                {acc.estimated_total_max.toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
