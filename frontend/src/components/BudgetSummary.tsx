import React from "react";
import { BudgetResultData } from "../types/trip";
import { WalletIcon } from "./Icons";

interface BudgetSummaryProps {
  budget: BudgetResultData;
}

export function BudgetSummary({ budget }: BudgetSummaryProps) {
  const { breakdown, budget_status, recommendations } = budget;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "within_budget":
        return (
          <span className="px-2.5 py-1 bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 text-xs font-semibold rounded-full">
            ● Within Budget
          </span>
        );
      case "near_budget":
        return (
          <span className="px-2.5 py-1 bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 text-xs font-semibold rounded-full">
            ● Near Budget
          </span>
        );
      case "over_budget":
        return (
          <span className="px-2.5 py-1 bg-rose-100 dark:bg-rose-950/80 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 text-xs font-semibold rounded-full">
            ● Over Budget
          </span>
        );
      default:
        return null;
    }
  };

  const categories = [
    { label: "Transport", min: breakdown.transport_min, max: breakdown.transport_max },
    { label: "Accommodation", min: breakdown.accommodation_min, max: breakdown.accommodation_max },
    { label: "Activities", min: breakdown.activities_min, max: breakdown.activities_max },
    { label: "Food & Dining", min: breakdown.food_min, max: breakdown.food_max },
    { label: "Local Travel", min: breakdown.local_travel_min, max: breakdown.local_travel_max },
    { label: "Miscellaneous", min: breakdown.miscellaneous_min, max: breakdown.miscellaneous_max },
  ];

  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800 rounded-2xl p-5 space-y-5 shadow-sm">
      <div className="flex items-center justify-between border-b border-neutral-100 dark:border-neutral-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400">
            <WalletIcon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-neutral-900 dark:text-white">
              Budget & Cost Breakdown
            </h3>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              Estimated totals & optimization analysis
            </p>
          </div>
        </div>

        {getStatusBadge(budget_status)}
      </div>

      {/* Summary Totals */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-neutral-50 dark:bg-neutral-950/60 p-4 rounded-xl border border-neutral-200/50 dark:border-neutral-800/50 text-xs">
        <div>
          <span className="text-neutral-500 dark:text-neutral-400 block text-[11px] uppercase tracking-wider font-semibold">
            Estimated Total Cost
          </span>
          <span className="text-base font-bold text-neutral-900 dark:text-white">
            ₹{breakdown.total_min.toLocaleString()} – ₹{breakdown.total_max.toLocaleString()}
          </span>
        </div>

        <div>
          <span className="text-neutral-500 dark:text-neutral-400 block text-[11px] uppercase tracking-wider font-semibold">
            Estimated Budget Delta (Remaining)
          </span>
          <span
            className={`text-base font-bold ${
              budget.remaining_min >= 0
                ? "text-emerald-600 dark:text-emerald-400"
                : "text-rose-600 dark:text-rose-400"
            }`}
          >
            {budget.remaining_min >= 0 ? "+" : ""}
            ₹{budget.remaining_min.toLocaleString()} to {budget.remaining_max >= 0 ? "+" : ""}
            ₹{budget.remaining_max.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Monetary Category Breakdown */}
      <div className="space-y-2.5">
        <div className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 uppercase tracking-wider">
          Category Estimates (INR)
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {categories.map((cat, idx) => (
            <div
              key={idx}
              className="flex justify-between items-center p-2.5 rounded-lg bg-neutral-50/70 dark:bg-neutral-950/40 border border-neutral-100 dark:border-neutral-800/60 text-xs"
            >
              <span className="text-neutral-600 dark:text-neutral-400 font-medium">
                {cat.label}
              </span>
              <span className="font-semibold text-neutral-900 dark:text-white">
                ₹{cat.min.toLocaleString()} – ₹{cat.max.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations Callout */}
      {recommendations && recommendations.length > 0 && (
        <div className="p-3.5 bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-200/60 dark:border-indigo-800/60 rounded-xl text-xs space-y-1.5 text-indigo-950 dark:text-indigo-200">
          <div className="font-semibold text-[11px] uppercase tracking-wider text-indigo-600 dark:text-indigo-400 flex items-center gap-1.5">
            <span>Optimization Suggestions</span>
          </div>
          <ul className="list-disc list-inside space-y-1 text-neutral-700 dark:text-neutral-300 leading-relaxed">
            {recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
