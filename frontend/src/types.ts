// Mirrors the backend Pydantic contract (kept hand-written; FastAPI doesn't
// emit a typed OpenAPI client in this project).

export type ExploitationType =
  | "agriculture" | "pv" | "wind" | "battery" | "data_center" | "undecided";

export interface Location { latitude: number; longitude: number; }

export interface ImageMetadata {
  height: number | null;
  width: number | null;
  bands: number | null;
  source_type: string | null;
}

export interface NDVIIndex {
  mean: number;
  median?: number | null;
  min?: number | null;
  max?: number | null;
  high_vegetation_percentage?: number | null;
}
export interface ScalarIndex { mean: number; }

export interface SpectralIndices {
  NDVI?: NDVIIndex | null;
  NDWI?: ScalarIndex | null;
  NDMI?: ScalarIndex | null;
  NDRE?: ScalarIndex | null;
  NBR?: ScalarIndex | null;
  GNDVI?: ScalarIndex | null;
}

export interface TerrainAnalysis {
  slope_degrees: number | null;
  terrain_suitability_score: number | null;
  terrain_limitation_label: string | null;
}

export interface InvestmentScores {
  agriculture_score: number;
  pv_score: number;
  wind_score: number;
  battery_score: number;
  data_center_score: number;
}

export interface RecommendedUse {
  final_recommendation: string | null;
  confidence: string | null;
}

export interface AgentReadySummary {
  one_liner: string | null;
  best_strategy: string | null;
}

export interface Property {
  property_id: string;
  plot_name: string;
  identity: string;
  region: string;
  location: Location;
  area_m2: number;
  price_eur: number;
  image_metadata: ImageMetadata;
  spectral_indices: SpectralIndices;
  terrain_analysis: TerrainAnalysis;
  investment_scores: InvestmentScores;
  recommended_use: RecommendedUse;
  suggested_crops: string[];
  risk_flags: string[];
  agent_ready_summary: AgentReadySummary;
  geometry?: unknown;
}

export interface UserProfile {
  user_id: string | null;
  intent: "land_investment_recommendation";
  exploitation_type: ExploitationType;
  preferred_region: string | null;
  budget: number | null;
  missing_fields: string[];
  profile_completed: boolean;
  notes: string | null;
}

export interface FinancialAnalysisItem {
  property_id: string;
  exploitation_type: string;
  estimated_initial_investment_eur: number;
  estimated_annual_revenue_eur: number;
  estimated_annual_operating_cost_eur: number;
  estimated_net_annual_profit_eur: number;
  estimated_payback_period_years: number;
  risk_level: "low" | "medium" | "high";
  risk_factors: string[];
  opportunities: string[];
  user_friendly_summary: string;
}
export interface FinancialAnalysis {
  financial_analysis: FinancialAnalysisItem[];
}

export interface FinalRecommendationCore {
  recommended_property_id: string;
  rank: number;
  confidence: number;
  reasoning_summary: string;
  main_reasons: string[];
  possible_concerns: string[];
}
export interface RankedProperty {
  property_id: string;
  rank: number;
  short_explanation: string;
}
export interface FinalRecommendation {
  final_recommendation: FinalRecommendationCore;
  ranked_properties: RankedProperty[];
  chatbot_final_response: string;
}

export type Stage =
  | "profiling" | "retrieving" | "financial" | "deciding" | "done";

export interface SessionState {
  session_id: string;
  stage: Stage;
  profile: UserProfile | null;
  candidates: Property[];
  financial: FinancialAnalysis | null;
  decision: FinalRecommendation | null;
}

// Best-fit exploitation derived from a property's scores. Used by the map +
// list cards before a recommendation exists.
export const SCORE_LABEL: Record<keyof InvestmentScores, string> = {
  agriculture_score: "Agriculture",
  pv_score: "Solar (PV)",
  wind_score: "Wind",
  battery_score: "Battery (BESS)",
  data_center_score: "Data Center",
};

export function bestScore(p: Property): { key: keyof InvestmentScores; value: number; label: string } {
  const entries = Object.entries(p.investment_scores) as [keyof InvestmentScores, number][];
  const top = entries.sort((a, b) => b[1] - a[1])[0];
  return { key: top[0], value: top[1], label: SCORE_LABEL[top[0]] };
}
