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

interface ParseResponse {
  status: "success" | "needs_information" | "error";
  trip?: TripData;
  duration_days?: number;
  duration_nights?: number;
  missing?: string[];
  error?: string;
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [message, setMessage] = useState<string>(
    "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [parseResult, setParseResult] = useState<ParseResponse | null>(null);
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

  const handleParseTrip = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setParseResult(null);
    setApiError(null);

    try {
      const res = await fetch(`${apiUrl}/api/trips/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await res.json();
      if (!res.ok) {
        setApiError(data.detail || "Failed to parse trip request.");
      } else {
        setParseResult(data);
      }
    } catch {
      setApiError("Unable to connect to backend service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 flex flex-col justify-between font-sans bg-white text-black max-w-3xl mx-auto">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tripwise</h1>
          <p className="text-gray-700 text-lg">AI-powered travel planning</p>
          <p className="text-sm text-gray-500">Phase 2 — Trip Input & Planner Agent</p>
        </div>

        <form onSubmit={handleParseTrip} className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Tell Tripwise about your trip
          </label>
          <textarea
            rows={4}
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
            {loading ? "Parsing..." : "Parse Trip"}
          </button>
        </form>

        {apiError && (
          <div className="p-4 border border-red-300 bg-red-50 text-red-700 text-sm rounded">
            {apiError}
          </div>
        )}

        {parseResult && parseResult.status === "needs_information" && (
          <div className="p-4 border border-amber-300 bg-amber-50 text-amber-800 text-sm rounded space-y-2">
            <p className="font-semibold">Missing Information Required</p>
            <p>Please specify the following missing parameters:</p>
            <ul className="list-disc list-inside font-mono text-xs">
              {parseResult.missing?.map((field) => (
                <li key={field}>{field}</li>
              ))}
            </ul>
          </div>
        )}

        {parseResult && parseResult.status === "success" && parseResult.trip && (
          <div className="p-4 border border-gray-200 rounded space-y-3">
            <h2 className="font-semibold text-lg border-b border-gray-200 pb-2">
              Trip Information
            </h2>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <span className="text-gray-500">Origin:</span>
              <span className="font-medium">{parseResult.trip.origin}</span>

              <span className="text-gray-500">Destination:</span>
              <span className="font-medium">{parseResult.trip.destination}</span>

              <span className="text-gray-500">Dates:</span>
              <span className="font-medium">
                {parseResult.trip.start_date} → {parseResult.trip.end_date}
              </span>

              <span className="text-gray-500">Budget:</span>
              <span className="font-medium">
                ₹{parseResult.trip.budget.toLocaleString()}
              </span>

              <span className="text-gray-500">Travelers:</span>
              <span className="font-medium">{parseResult.trip.travelers}</span>

              <span className="text-gray-500">Duration:</span>
              <span className="font-medium">
                {parseResult.duration_days} days / {parseResult.duration_nights} nights
              </span>

              {parseResult.trip.preferences.length > 0 && (
                <>
                  <span className="text-gray-500">Preferences:</span>
                  <span className="font-medium">
                    {parseResult.trip.preferences.join(", ")}
                  </span>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 pt-4 mt-8 text-sm text-gray-600">
        Backend Status: <span className="font-semibold">{backendStatus}</span>
      </div>
    </main>
  );
}
