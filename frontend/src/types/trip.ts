export interface TripRequest {
  origin: string;
  destination: string;
  start_date: string;
  end_date: string;
  budget: number;
  travelers: number;
  preferences: string[];
}

export interface TransportOptionData {
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

export interface AccommodationOptionData {
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

export interface DestinationPlaceData {
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

export interface BudgetBreakdownData {
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

export type BudgetStatus = "within_budget" | "near_budget" | "over_budget";

export interface BudgetResultData {
  budget: number;
  breakdown: BudgetBreakdownData;
  budget_status: BudgetStatus;
  remaining_min: number;
  remaining_max: number;
  recommendations: string[];
  is_estimate: boolean;
}

export interface ItineraryActivityData {
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

export interface ItineraryDayData {
  day_number: number;
  date: string;
  title: string;
  activities: ItineraryActivityData[];
  estimated_day_cost_min: number;
  estimated_day_cost_max: number;
}

export interface ItineraryResultData {
  destination: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  days: ItineraryDayData[];
  total_activity_cost_min: number;
  total_activity_cost_max: number;
  is_estimate: boolean;
}

export interface FullPlanResponse {
  status: "success" | "needs_information" | "needs_clarification" | "error";
  trip?: TripRequest;
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
  intent?: Record<string, any>;
  message?: string;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  content: string;
  timestamp: string;
  plan?: FullPlanResponse;
  modificationResult?: {
    status: string;
    message?: string;
    intent?: Record<string, any>;
  };
  isError?: boolean;
  missing?: string[];
}
