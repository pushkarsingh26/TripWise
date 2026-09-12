"use client";

import { useEffect, useState, useRef } from "react";
import { Header } from "../components/Header";
import { Composer } from "../components/Composer";
import { SuggestionPrompts } from "../components/SuggestionPrompts";
import { MessageBubble } from "../components/MessageBubble";
import { LoadingState } from "../components/LoadingState";
import { ChatMessage, FullPlanResponse, TripRequest } from "../types/trip";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMsg, setLoadingMsg] = useState<string>("Tripwise is planning your trip...");
  const [currentTripRequest, setCurrentTripRequest] = useState<TripRequest | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Check health status on load
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

  // Auto scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleResetTrip = () => {
    setMessages([]);
    setCurrentTripRequest(null);
    setInputMessage("");
    setLoading(false);
  };

  const handleSelectPrompt = (promptText: string) => {
    setInputMessage(promptText);
    executeSendMessage(promptText);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;
    const textToSend = inputMessage.trim();
    setInputMessage("");
    executeSendMessage(textToSend);
  };

  const executeSendMessage = async (userPrompt: string) => {
    const userMsgId = `user-${Date.now()}`;
    const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    const userMessage: ChatMessage = {
      id: userMsgId,
      sender: "user",
      content: userPrompt,
      timestamp,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      if (!currentTripRequest) {
        // --- INITIAL TRIP PLANNING FLOW ---
        // Step A: Parse natural-language input into structured request
        setLoadingMsg("Parsing trip parameters...");
        const parseRes = await fetch(`${apiUrl}/api/trips/parse`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userPrompt }),
        });

        const parseData = await parseRes.json();

        if (!parseRes.ok) {
          const assistantMsg: ChatMessage = {
            id: `assistant-${Date.now()}`,
            sender: "assistant",
            content: parseData.detail || "Unable to understand trip parameters. Please clarify your request.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            isError: true,
          };
          setMessages((prev) => [...prev, assistantMsg]);
          return;
        }

        if (parseData.status === "needs_information") {
          const assistantMsg: ChatMessage = {
            id: `assistant-${Date.now()}`,
            sender: "assistant",
            content: "I need a little more information before I can plan this trip.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            missing: parseData.missing,
          };
          setMessages((prev) => [...prev, assistantMsg]);
          return;
        }

        // Step B: Send structured trip request to /plan endpoint
        const structuredTrip: TripRequest = parseData.trip;
        setLoadingMsg("Generating full trip plan & itinerary...");

        const planRes = await fetch(`${apiUrl}/api/trips/plan`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trip: structuredTrip }),
        });

        const planData: FullPlanResponse = await planRes.json();

        if (!planRes.ok || planData.status === "error") {
          const assistantMsg: ChatMessage = {
            id: `assistant-${Date.now()}`,
            sender: "assistant",
            content: planData.error || "Tripwise encountered an issue while generating your trip plan. Please try again.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            isError: true,
          };
          setMessages((prev) => [...prev, assistantMsg]);
          return;
        }

        if (planData.status === "success" && planData.trip) {
          setCurrentTripRequest(planData.trip);

          const assistantMsg: ChatMessage = {
            id: `assistant-${Date.now()}`,
            sender: "assistant",
            content: `Here is your trip plan for ${planData.trip.destination}! I have optimized transport, accommodation, budget breakdown, and day-by-day itinerary below.`,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            plan: planData,
          };
          setMessages((prev) => [...prev, assistantMsg]);
        }
      } else {
        // --- CONVERSATIONAL MODIFICATION FLOW ---
        setLoadingMsg("Updating your trip plan...");

        const modifyRes = await fetch(`${apiUrl}/api/trips/modify`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userPrompt,
            trip: currentTripRequest,
          }),
        });

        const modifyData = await modifyRes.json();

        if (!modifyRes.ok) {
          const assistantMsg: ChatMessage = {
            id: `assistant-${Date.now()}`,
            sender: "assistant",
            content: modifyData.detail || "Tripwise couldn't update your trip right now. Please try again.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            isError: true,
          };
          setMessages((prev) => [...prev, assistantMsg]);
          return;
        }

        if (modifyData.status === "needs_clarification") {
          const assistantMsg: ChatMessage = {
            id: `assistant-${Date.now()}`,
            sender: "assistant",
            content: modifyData.message || "Request is ambiguous. Please clarify your modification.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            modificationResult: {
              status: "needs_clarification",
              message: modifyData.message,
              intent: modifyData.intent,
            },
          };
          setMessages((prev) => [...prev, assistantMsg]);
          return;
        }

        if (modifyData.status === "success" && modifyData.plan && modifyData.trip) {
          setCurrentTripRequest(modifyData.trip);

          const updatedPlanResponse: FullPlanResponse = {
            status: "success",
            trip: modifyData.trip,
            duration_days: modifyData.plan.duration_days,
            duration_nights: modifyData.plan.duration_nights,
            transport: modifyData.plan.transport,
            accommodation: modifyData.plan.accommodation,
            destination: modifyData.plan.destination,
            budget: modifyData.plan.budget,
            itinerary: modifyData.plan.itinerary,
          };

          const assistantMsg: ChatMessage = {
            id: `assistant-${Date.now()}`,
            sender: "assistant",
            content: modifyData.message || "Updated your trip plan according to your preferences!",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            plan: updatedPlanResponse,
            modificationResult: {
              status: "success",
              message: modifyData.message,
              intent: modifyData.intent,
            },
          };
          setMessages((prev) => [...prev, assistantMsg]);
        }
      }
    } catch {
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: "assistant",
        content: "Unable to connect to Tripwise services. Please ensure the backend server is running and try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        isError: true,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-neutral-950">
      <Header
        backendStatus={backendStatus}
        onNewTrip={handleResetTrip}
        hasActiveTrip={messages.length > 0}
      />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col">
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <SuggestionPrompts onSelectPrompt={handleSelectPrompt} />
          </div>
        ) : (
          <div className="flex-1 space-y-4 pb-4">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {loading && <LoadingState message={loadingMsg} />}

            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      <Composer
        inputMessage={inputMessage}
        setInputMessage={setInputMessage}
        onSubmit={handleFormSubmit}
        isLoading={loading}
        hasActiveTrip={currentTripRequest !== null}
      />
    </div>
  );
}
