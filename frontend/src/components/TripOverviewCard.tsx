import React from "react";
import { TripRequest } from "../types/trip";
import { CalendarIcon, MapPinIcon, UsersIcon, WalletIcon } from "./Icons";

interface TripOverviewCardProps {
  trip: TripRequest;
  durationDays?: number;
  durationNights?: number;
}

export function TripOverviewCard({
  trip,
  durationDays,
  durationNights,
}: TripOverviewCardProps) {
  return (
    <div className="bg-gradient-to-br from-indigo-900 via-indigo-950 to-neutral-950 text-white rounded-2xl p-5 shadow-lg space-y-4 border border-indigo-800/40">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-indigo-800/50 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-300">
            <MapPinIcon className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-indigo-200 uppercase tracking-wider font-semibold">
              Route
            </div>
            <div className="text-lg font-bold tracking-tight">
              {trip.origin} <span className="text-indigo-400 font-normal">→</span> {trip.destination}
            </div>
          </div>
        </div>

        {durationDays && (
          <div className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 text-xs font-semibold">
            {durationDays} Days / {durationNights} Nights
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
        <div className="flex items-center gap-2.5">
          <CalendarIcon className="w-4 h-4 text-indigo-400 shrink-0" />
          <div>
            <span className="text-indigo-300/80 block">Travel Dates</span>
            <span className="font-semibold text-white">
              {trip.start_date} → {trip.end_date}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <UsersIcon className="w-4 h-4 text-indigo-400 shrink-0" />
          <div>
            <span className="text-indigo-300/80 block">Travelers</span>
            <span className="font-semibold text-white">
              {trip.travelers} {trip.travelers === 1 ? "Person" : "People"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <WalletIcon className="w-4 h-4 text-indigo-400 shrink-0" />
          <div>
            <span className="text-indigo-300/80 block">Target Budget</span>
            <span className="font-semibold text-white text-sm">
              ₹{trip.budget.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {trip.preferences && trip.preferences.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {trip.preferences.map((pref, idx) => (
            <span
              key={idx}
              className="text-[11px] px-2.5 py-0.5 rounded-md bg-white/10 text-indigo-100 font-medium backdrop-blur-sm"
            >
              #{pref}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
