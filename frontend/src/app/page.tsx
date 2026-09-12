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

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [message, setMessage] = useState<string>(
    "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [optionsResult, setOptionsResult] = useState<OptionsResponse | null>(null);
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

  const handleGetOptions = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setOptionsResult(null);
    setApiError(null);

    try {
      const res = await fetch(`${apiUrl}/api/trips/options`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await res.json();
      if (!res.ok) {
        setApiError(data.detail || "Failed to fetch trip options.");
      } else {
        setOptionsResult(data);
      }
    } catch {
      setApiError("Unable to connect to backend service.");
    } finally {
      setLoading(false);
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
            Phase 3 — Transport & Accommodation Agents
          </p>
        </div>

        <form onSubmit={handleGetOptions} className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Tell Tripwise about your trip
          </label>
          <textarea
            rows={3}
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-black text-black bg-white"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="e.g. I want to travel from Indore to Goa from Oct 10 to Oct 15 with a budget of 30000 for 2 people."
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-black text-white rounded font-medium disabled:opacity-50"
          >
            {loading ? "Calculating Options..." : "Get Trip Options"}
          </button>
        </form>

        {apiError && (
          <div className="p-4 border border-red-300 bg-red-50 text-red-700 text-sm rounded">
            {apiError}
          </div>
        )}

        {optionsResult && optionsResult.status === "needs_information" && (
          <div className="p-4 border border-amber-300 bg-amber-50 text-amber-800 text-sm rounded space-y-2">
            <p className="font-semibold">Missing Information Required</p>
            <p>Please specify the following missing parameters:</p>
            <ul className="list-disc list-inside font-mono text-xs">
              {optionsResult.missing?.map((field) => (
                <li key={field}>{field}</li>
              ))}
            </ul>
          </div>
        )}

        {optionsResult && optionsResult.status === "success" && optionsResult.trip && (
          <div className="space-y-6">
            {/* Trip Summary */}
            <div className="p-4 border border-gray-200 rounded space-y-3">
              <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
                Trip Information
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
                <div>
                  <span className="text-gray-500 block text-xs">Origin</span>
                  <span className="font-medium">{optionsResult.trip.origin}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Destination</span>
                  <span className="font-medium">{optionsResult.trip.destination}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Dates</span>
                  <span className="font-medium">
                    {optionsResult.trip.start_date} → {optionsResult.trip.end_date}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Budget</span>
                  <span className="font-medium">
                    ₹{optionsResult.trip.budget.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Travelers</span>
                  <span className="font-medium">{optionsResult.trip.travelers}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-xs">Duration</span>
                  <span className="font-medium">
                    {optionsResult.duration_days} days / {optionsResult.duration_nights} nights
                  </span>
                </div>
              </div>
            </div>

            {/* Transport Options */}
            {optionsResult.transport && (
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
                      <div className="text-gray-500 text-xs">
                        Duration: {opt.duration} • Comfort: {opt.comfort_level}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Accommodation Options */}
            {optionsResult.accommodation && (
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
                      <div className="text-gray-600">
                        ₹{acc.estimated_price_per_night_min.toLocaleString()} – ₹
                        {acc.estimated_price_per_night_max.toLocaleString()} / night
                      </div>
                      <div className="text-gray-800 font-medium">
                        Total Stay ({optionsResult.accommodation?.nights} nights): ₹
                        {acc.estimated_total_min.toLocaleString()} – ₹
                        {acc.estimated_total_max.toLocaleString()}
                      </div>
                      <div className="text-gray-500 text-xs">
                        {acc.location_description}
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
