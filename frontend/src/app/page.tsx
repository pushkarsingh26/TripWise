"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
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
  }, []);

  return (
    <main className="min-h-screen p-8 flex flex-col justify-between font-sans bg-white text-black">
      <div className="space-y-4 max-w-xl">
        <h1 className="text-3xl font-bold tracking-tight">Tripwise</h1>
        <p className="text-lg text-gray-700">AI-powered travel planning</p>
        <p className="text-sm text-gray-500">Phase 1 foundation is running.</p>
      </div>

      <div className="border-t border-gray-200 pt-4 text-sm text-gray-600">
        Backend Status: <span className="font-semibold">{backendStatus}</span>
      </div>
    </main>
  );
}
