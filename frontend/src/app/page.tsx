"use client";

import { useEffect, useState } from "react";

interface TripData {
  origin: string;
  destination: string;
  start_date: string;
  end_date: string;
  budget: number;
  travelers: number;
  preferences: string[];
}

interface TransportOptionData {
  mode: string;
  estimated_cost_min: number;
  estimated_cost_max: number;
  currency: string;
  pricing_type: string;
  duration: string;
  comfort_level: string;
  recommendation_type: string;
  pros: string[];
  cons: string[];
  is_estimate: boolean;
}

interface AccommodationOptionData {
  name: string;
  category: string;
  estimated_price_per_night_min: number;
  estimated_price_per_night_max: number;
  estimated_total_min: number;
  estimated_total_max: number;
  currency: string;
  location_description: string;
  rating?: number;
  amenities: string[];
  is_estimate: boolean;
}

interface DestinationPlaceData {
  name: string;
  category: string;
  description: string;
  estimated_cost_min: number;
  estimated_cost_max: number;
  currency: string;
  recommended_duration: string;
  best_for: string[];
  is_estimate: boolean;
}

interface BudgetBreakdownData {
  transport_min: number;
  transport_max: number;
  accommodation_min: number;
  accommodation_max: number;
  activities_min: number;
  activities_max: number;
  food_min: number;
  food_max: number;
  local_travel_min: number;
  local_travel_max: number;
  miscellaneous_min: number;
  miscellaneous_max: number;
  total_min: number;
  total_max: number;
  currency: string;
  is_estimate: boolean;
}

interface BudgetResultData {
  budget: number;
  breakdown: BudgetBreakdownData;
  budget_status: "within_budget" | "near_budget" | "over_budget";
  remaining_min: number;
  remaining_max: number;
  recommendations: string[];
  is_estimate: boolean;
}

interface ItineraryActivityData {
  name: string;
  category: string;
  description: string;
  start_time: string;
  end_time: string;
  duration: string;
  estimated_cost_min: number;
  estimated_cost_max: number;
  is_estimate: boolean;
}

interface ItineraryDayData {
  day_number: number;
  date: string;
  title: string;
  activities: ItineraryActivityData[];
  estimated_day_cost_min: number;
  estimated_day_cost_max: number;
}

interface ItineraryResultData {
  destination: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  days: ItineraryDayData[];
  total_activity_cost_min: number;
  total_activity_cost_max: number;
  is_estimate: boolean;
}

interface FullPlanResponse {
  status: "success" | "needs_information" | "error";
  trip?: TripData;
  duration_days?: number;
  duration_nights?: number;
  transport?: {
    origin: string;
    destination: string;
    options: TransportOptionData[];
  };
  accommodation?: {
    destination: string;
    nights: number;
    options: AccommodationOptionData[];
  };
  destination?: {
    destination: string;
    supported: boolean;
    message?: string;
    recommendations: DestinationPlaceData[];
  };
  budget?: BudgetResultData;
  itinerary?: ItineraryResultData;
  missing?: string[];
  error?: string;
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [message, setMessage] = useState<string>(
    "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people. I love beaches and food."
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [planResult, setPlanResult] = useState<FullPlanResponse | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.status === "healthy") {
          setBackendStatus("Connected");
        } else {
          setBackendStatus("Disconnected");
        }
      })
      .catch(() => {
        setBackendStatus("Disconnected");
      });
  }, [apiUrl]);

  const handleGeneratePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setPlanResult(null);
    setApiError(null);

    try {
      const res = await fetch(`${apiUrl}/api/trips/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await res.json();
      if (!res.ok) {
        setApiError(data.detail || "Failed to generate trip plan.");
      } else {
        setPlanResult(data);
      }
    } catch {
      setApiError("Unable to connect to backend service.");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "within_budget":
        return (
          <span className="px-2.5 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
            Within Budget
          </span>
        );
      case "near_budget":
        return (
          <span className="px-2.5 py-1 bg-amber-100 text-amber-800 text-xs font-semibold rounded">
            Near Budget
          </span>
        );
      case "over_budget":
        return (
          <span className="px-2.5 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded">
            Over Budget
          </span>
        );
      default:
        return null;
    }
  };

  const getModeIcon = (mode: string) => {
    switch (mode) {
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
    <main className="min-h-screen p-8 flex flex-col justify-between font-sans bg-white text-black max-w-4xl mx-auto">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tripwise</h1>
          <p className="text-gray-700 text-lg">AI-powered travel planning</p>
          <p className="text-sm text-gray-500">
            Phase 6 — Itinerary Agent + Multi-Agent Orchestration
          </p>
        </div>

        <form onSubmit={handleGeneratePlan} className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Tell Tripwise about your trip
          </label>
          <textarea
            rows={3}
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-black text-black bg-white"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="e.g. I want to travel from Indore to Goa from Oct 10 to Oct 15 with a budget of 30000 for 2 people. I love beaches and food."
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 bg-black text-white rounded font-medium disabled:opacity-50"
          >
            {loading ? "Orchestrating Plan..." : "Generate Full Trip Plan"}
          </button>
        </form>

        {apiError && (
          <div className="p-4 border border-red-300 bg-red-50 text-red-700 text-sm rounded">
            {apiError}
          </div>
        )}

        {planResult && planResult.status === "needs_information" && (
          <div className="p-4 border border-amber-300 bg-amber-50 text-amber-800 text-sm rounded space-y-2">
            <p className="font-semibold">Missing Information Required</p>
            <p>Please specify the following missing parameters:</p>
            <ul className="list-disc list-inside font-mono text-xs">
              {planResult.missing?.map((field) => (
                <li key={field}>{field}</li>
              ))}
            </ul>
          </div>
        )}

        {planResult && planResult.status === "success" && planResult.trip && (
          <div className="space-y-6">
            {/* Trip Summary */}
            <div className="p-4 border border-gray-200 rounded space-y-3">
              <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
                Trip Information
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
                <div>
                  <span className="text-gray-500 block text-xs">Origin</span>
                  <span className="font-medium">{planResult.trip.origin}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Destination</span>
                  <span className="font-medium">{planResult.trip.destination}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Dates</span>
                  <span className="font-medium">
                    {planResult.trip.start_date} → {planResult.trip.end_date}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Target Budget</span>
                  <span className="font-medium">
                    ₹{planResult.trip.budget.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Travelers</span>
                  <span className="font-medium">{planResult.trip.travelers}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Duration</span>
                  <span className="font-medium">
                    {planResult.duration_days} days / {planResult.duration_nights} nights
                  </span>
                </div>
              </div>
            </div>

            {/* Day-by-Day Itinerary */}
            {planResult.itinerary && (
              <div className="p-4 border border-gray-200 rounded space-y-4">
                <div className="flex justify-between items-center border-b border-gray-200 pb-2">
                  <h2 className="font-semibold text-lg">Day-by-Day Itinerary</h2>
                  {planResult.itinerary.is_estimate && (
                    <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-normal">
                      Illustrative Estimate
                    </span>
                  )}
                </div>

                <div className="space-y-4">
                  {planResult.itinerary.days.map((day) => (
                    <div
                      key={day.day_number}
                      className="border border-gray-200 rounded p-4 space-y-3 bg-gray-50/50"
                    >
                      <div className="flex justify-between items-center font-medium border-b border-gray-200 pb-1 text-sm">
                        <span>
                          {day.title} ({day.date})
                        </span>
                        <span className="text-xs text-gray-500">
                          Est. Day Activity Cost: ₹
                          {day.estimated_day_cost_min.toLocaleString()} – ₹
                          {day.estimated_day_cost_max.toLocaleString()}
                        </span>
                      </div>

                      {day.activities.length === 0 ? (
                        <p className="text-xs text-gray-500 italic">
                          Free time / Exploration day
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {day.activities.map((act, idx) => (
                            <div
                              key={idx}
                              className="p-3 bg-white border border-gray-200 rounded text-sm space-y-1"
                            >
                              <div className="flex justify-between items-center font-medium">
                                <span className="flex gap-2 items-center">
                                  <span className="text-xs px-2 py-0.5 bg-black text-white rounded font-mono">
                                    {act.start_time} – {act.end_time}
                                  </span>
                                  <span>{act.name}</span>
                                </span>
                                <span className="text-xs px-2 py-0.5 bg-gray-200 rounded text-gray-700 capitalize">
                                  {act.category}
                                </span>
                              </div>
                              <p className="text-gray-600 text-xs">{act.description}</p>
                              <div className="text-gray-500 text-xs flex justify-between pt-1">
                                <span>Duration: {act.duration}</span>
                                <span>
                                  Est. Cost: ₹{act.estimated_cost_min.toLocaleString()} – ₹
                                  {act.estimated_cost_max.toLocaleString()}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Budget Engine Breakdown & Optimization */}
            {planResult.budget && (
              <div className="p-4 border border-gray-200 rounded space-y-4">
                <div className="flex justify-between items-center border-b border-gray-200 pb-2">
                  <div className="flex items-center gap-3">
                    <h2 className="font-semibold text-lg">Budget Breakdown</h2>
                    {getStatusBadge(planResult.budget.budget_status)}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm bg-gray-50 p-3 rounded">
                  <div>
                    <span className="text-gray-500 block text-xs">Estimated Total Range</span>
                    <span className="font-semibold text-base">
                      ₹{planResult.budget.breakdown.total_min.toLocaleString()} – ₹
                      {planResult.budget.breakdown.total_max.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-xs">
                      Estimated Budget Balance (Remaining Delta)
                    </span>
                    <span className="font-semibold text-base">
                      {planResult.budget.remaining_min >= 0 ? "+" : ""}
                      ₹{planResult.budget.remaining_min.toLocaleString()} to{" "}
                      {planResult.budget.remaining_max >= 0 ? "+" : ""}
                      ₹{planResult.budget.remaining_max.toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* Recommendations */}
                {planResult.budget.recommendations.length > 0 && (
                  <div className="p-3 bg-blue-50 border border-blue-200 text-blue-900 rounded space-y-1">
                    <p className="font-semibold text-xs uppercase tracking-wide">
                      Budget Optimization Suggestions
                    </p>
                    <ul className="list-disc list-inside text-xs space-y-1">
                      {planResult.budget.recommendations.map((tip, idx) => (
                        <li key={idx}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Transport Options */}
            {planResult.transport && (
              <div className="p-4 border border-gray-200 rounded space-y-4">
                <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
                  Transport Options
                </h2>
                <div className="space-y-3">
                  {planResult.transport.options.map((opt) => (
                    <div
                      key={opt.mode}
                      className="p-3 border border-gray-100 bg-gray-50 rounded text-sm space-y-1"
                    >
                      <div className="flex justify-between items-center font-medium">
                        <span>{getModeIcon(opt.mode)}</span>
                        <div className="flex gap-2 items-center">
                          <span className="text-xs px-2 py-0.5 bg-gray-200 rounded text-gray-700 capitalize">
                            Best for: {opt.recommendation_type}
                          </span>
                          {opt.is_estimate && (
                            <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-normal">
                              Estimate
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-gray-600">
                        Estimated Cost: ₹{opt.estimated_cost_min.toLocaleString()} – ₹
                        {opt.estimated_cost_max.toLocaleString()} ({opt.pricing_type})
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Accommodation Options */}
            {planResult.accommodation && (
              <div className="p-4 border border-gray-200 rounded space-y-4">
                <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
                  Accommodation Options ({planResult.accommodation.nights} nights)
                </h2>
                <div className="space-y-3">
                  {planResult.accommodation.options.map((acc) => (
                    <div
                      key={acc.category}
                      className="p-3 border border-gray-100 bg-gray-50 rounded text-sm space-y-1"
                    >
                      <div className="flex justify-between items-center font-medium">
                        <span>{acc.name}</span>
                        {acc.is_estimate && (
                          <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-normal">
                            Estimate
                          </span>
                        )}
                      </div>
                      <div className="text-gray-800 font-medium">
                        Total Stay ({planResult.accommodation?.nights} nights): ₹
                        {acc.estimated_total_min.toLocaleString()} – ₹
                        {acc.estimated_total_max.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 pt-4 mt-8 text-sm text-gray-600">
        Backend Status: <span className="font-semibold">{backendStatus}</span>
      </div>
    </main>
  );
}
