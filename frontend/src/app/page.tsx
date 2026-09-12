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

interface BudgetResponse {
  status: "success" | "needs_information" | "error";
  trip?: TripData;
  duration_days?: number;
  duration_nights?: number;
  budget?: BudgetResultData;
  missing?: string[];
  error?: string;
}

interface OptionsResponse {
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
  missing?: string[];
  error?: string;
}

interface DestinationsResponse {
  status: "success" | "needs_information" | "error";
  trip?: TripData;
  destination?: {
    destination: string;
    supported: boolean;
    message?: string;
    recommendations: DestinationPlaceData[];
  };
  missing?: string[];
  error?: string;
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [message, setMessage] = useState<string>(
    "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people. I love beaches and food."
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [budgetResult, setBudgetResult] = useState<BudgetResponse | null>(null);
  const [optionsResult, setOptionsResult] = useState<OptionsResponse | null>(null);
  const [destinationsResult, setDestinationsResult] =
    useState<DestinationsResponse | null>(null);
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

  const handleGetFullPlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setBudgetResult(null);
    setOptionsResult(null);
    setDestinationsResult(null);
    setApiError(null);

    try {
      const [budRes, optRes, destRes] = await Promise.all([
        fetch(`${apiUrl}/api/trips/budget`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        }),
        fetch(`${apiUrl}/api/trips/options`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        }),
        fetch(`${apiUrl}/api/trips/destinations`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        }),
      ]);

      const budData = await budRes.json();
      const optData = await optRes.json();
      const destData = await destRes.json();

      if (!budRes.ok) {
        setApiError(budData.detail || "Failed to calculate budget.");
      } else {
        setBudgetResult(budData);
        setOptionsResult(optData);
        setDestinationsResult(destData);
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
            Phase 5 — Budget Engine + Optimization
          </p>
        </div>

        <form onSubmit={handleGetFullPlan} className="space-y-4">
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
            className="px-4 py-2 bg-black text-white rounded font-medium disabled:opacity-50"
          >
            {loading ? "Analyzing Budget..." : "Calculate Budget & Options"}
          </button>
        </form>

        {apiError && (
          <div className="p-4 border border-red-300 bg-red-50 text-red-700 text-sm rounded">
            {apiError}
          </div>
        )}

        {budgetResult && budgetResult.status === "needs_information" && (
          <div className="p-4 border border-amber-300 bg-amber-50 text-amber-800 text-sm rounded space-y-2">
            <p className="font-semibold">Missing Information Required</p>
            <p>Please specify the following missing parameters:</p>
            <ul className="list-disc list-inside font-mono text-xs">
              {budgetResult.missing?.map((field) => (
                <li key={field}>{field}</li>
              ))}
            </ul>
          </div>
        )}

        {budgetResult && budgetResult.status === "success" && budgetResult.budget && (
          <div className="space-y-6">
            {/* Trip Summary */}
            {budgetResult.trip && (
              <div className="p-4 border border-gray-200 rounded space-y-3">
                <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
                  Trip Information
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
                  <div>
                    <span className="text-gray-500 block text-xs">Origin</span>
                    <span className="font-medium">{budgetResult.trip.origin}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-xs">Destination</span>
                    <span className="font-medium">
                      {budgetResult.trip.destination}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-xs">Dates</span>
                    <span className="font-medium">
                      {budgetResult.trip.start_date} → {budgetResult.trip.end_date}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-xs">Target Budget</span>
                    <span className="font-medium">
                      ₹{budgetResult.trip.budget.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-xs">Travelers</span>
                    <span className="font-medium">{budgetResult.trip.travelers}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-xs">Duration</span>
                    <span className="font-medium">
                      {budgetResult.duration_days} days / {budgetResult.duration_nights} nights
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Budget Engine Breakdown & Optimization */}
            <div className="p-4 border border-gray-200 rounded space-y-4">
              <div className="flex justify-between items-center border-b border-gray-200 pb-2">
                <div className="flex items-center gap-3">
                  <h2 className="font-semibold text-lg">Budget Breakdown</h2>
                  {getStatusBadge(budgetResult.budget.budget_status)}
                </div>
                {budgetResult.budget.is_estimate && (
                  <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-normal">
                    Illustrative Estimate
                  </span>
                )}
              </div>

              {/* Range & Delta */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm bg-gray-50 p-3 rounded">
                <div>
                  <span className="text-gray-500 block text-xs">Estimated Total Range</span>
                  <span className="font-semibold text-base">
                    ₹{budgetResult.budget.breakdown.total_min.toLocaleString()} – ₹
                    {budgetResult.budget.breakdown.total_max.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">
                    Estimated Budget Balance (Remaining Delta)
                  </span>
                  <span className="font-semibold text-base">
                    {budgetResult.budget.remaining_min >= 0 ? "+" : ""}
                    ₹{budgetResult.budget.remaining_min.toLocaleString()} to{" "}
                    {budgetResult.budget.remaining_max >= 0 ? "+" : ""}
                    ₹{budgetResult.budget.remaining_max.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Category Breakdown Table */}
              <div className="text-sm space-y-1">
                <div className="grid grid-cols-2 text-xs font-semibold text-gray-500 border-b pb-1">
                  <span>Category</span>
                  <span className="text-right">Estimated Cost</span>
                </div>

                <div className="grid grid-cols-2 py-1 border-b border-gray-100">
                  <span>Transport ({budgetResult.trip?.travelers} travelers)</span>
                  <span className="text-right font-medium">
                    ₹{budgetResult.budget.breakdown.transport_min.toLocaleString()} – ₹
                    {budgetResult.budget.breakdown.transport_max.toLocaleString()}
                  </span>
                </div>

                <div className="grid grid-cols-2 py-1 border-b border-gray-100">
                  <span>Accommodation ({budgetResult.duration_nights} nights)</span>
                  <span className="text-right font-medium">
                    ₹{budgetResult.budget.breakdown.accommodation_min.toLocaleString()} – ₹
                    {budgetResult.budget.breakdown.accommodation_max.toLocaleString()}
                  </span>
                </div>

                <div className="grid grid-cols-2 py-1 border-b border-gray-100">
                  <span>Activities (Top subset × travelers)</span>
                  <span className="text-right font-medium">
                    ₹{budgetResult.budget.breakdown.activities_min.toLocaleString()} – ₹
                    {budgetResult.budget.breakdown.activities_max.toLocaleString()}
                  </span>
                </div>

                <div className="grid grid-cols-2 py-1 border-b border-gray-100">
                  <span>Food (₹500–₹1000/person/day)</span>
                  <span className="text-right font-medium">
                    ₹{budgetResult.budget.breakdown.food_min.toLocaleString()} – ₹
                    {budgetResult.budget.breakdown.food_max.toLocaleString()}
                  </span>
                </div>

                <div className="grid grid-cols-2 py-1 border-b border-gray-100">
                  <span>Local Travel (₹200–₹500/person/day)</span>
                  <span className="text-right font-medium">
                    ₹{budgetResult.budget.breakdown.local_travel_min.toLocaleString()} – ₹
                    {budgetResult.budget.breakdown.local_travel_max.toLocaleString()}
                  </span>
                </div>

                <div className="grid grid-cols-2 py-1 border-b border-gray-100">
                  <span>Miscellaneous (₹100–₹300/person/day)</span>
                  <span className="text-right font-medium">
                    ₹{budgetResult.budget.breakdown.miscellaneous_min.toLocaleString()} – ₹
                    {budgetResult.budget.breakdown.miscellaneous_max.toLocaleString()}
                  </span>
                </div>

                <div className="grid grid-cols-2 py-2 font-bold text-base pt-2">
                  <span>Total Estimated Trip Cost</span>
                  <span className="text-right">
                    ₹{budgetResult.budget.breakdown.total_min.toLocaleString()} – ₹
                    {budgetResult.budget.breakdown.total_max.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Optimization Recommendations */}
              {budgetResult.budget.recommendations.length > 0 && (
                <div className="p-3 bg-blue-50 border border-blue-200 text-blue-900 rounded space-y-1">
                  <p className="font-semibold text-xs uppercase tracking-wide">
                    Budget Optimization Suggestions
                  </p>
                  <ul className="list-disc list-inside text-xs space-y-1">
                    {budgetResult.budget.recommendations.map((tip, idx) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Destination Recommendations */}
            {destinationsResult && destinationsResult.destination && (
              <div className="p-4 border border-gray-200 rounded space-y-4">
                <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
                  Destination Recommendations ({destinationsResult.destination.destination})
                </h2>

                {!destinationsResult.destination.supported ? (
                  <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    {destinationsResult.destination.message}
                  </p>
                ) : (
                  <div className="space-y-3">
                    {destinationsResult.destination.recommendations.map((place) => (
                      <div
                        key={place.name}
                        className="p-3 border border-gray-100 bg-gray-50 rounded text-sm space-y-1"
                      >
                        <div className="flex justify-between items-center font-medium">
                          <span>{place.name}</span>
                          <div className="flex gap-2 items-center">
                            <span className="text-xs px-2 py-0.5 bg-gray-200 rounded text-gray-700 capitalize">
                              {place.category}
                            </span>
                            {place.is_estimate && (
                              <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-normal">
                                Estimate
                              </span>
                            )}
                          </div>
                        </div>
                        <p className="text-gray-700 text-xs">{place.description}</p>
                        <div className="text-gray-600 text-xs flex gap-4">
                          <span>
                            Estimated Cost: ₹{place.estimated_cost_min.toLocaleString()} – ₹
                            {place.estimated_cost_max.toLocaleString()}
                          </span>
                          <span>Duration: {place.recommended_duration}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Transport Options */}
            {optionsResult && optionsResult.transport && (
              <div className="p-4 border border-gray-200 rounded space-y-4">
                <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
                  Transport Options
                </h2>
                <div className="space-y-3">
                  {optionsResult.transport.options.map((opt) => (
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
            {optionsResult && optionsResult.accommodation && (
              <div className="p-4 border border-gray-200 rounded space-y-4">
                <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
                  Accommodation Options ({optionsResult.accommodation.nights} nights)
                </h2>
                <div className="space-y-3">
                  {optionsResult.accommodation.options.map((acc) => (
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
                        Total Stay ({optionsResult.accommodation?.nights} nights): ₹
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
