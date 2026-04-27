export type CIDataSource = "real_scraping" | "precomputed_demo" | "provided_data";

export type InterpretationStatus =
  | "BLOCKED_FOR_CAUSAL_INTERPRETATION"
  | "WARNING"
  | "USE_WITH_CAUTION"
  | "OUTLIER_MONITORING";

export interface ReportKPI {
  metric: string;
  value: string;
  delta: string;
  direction: "up" | "down" | "flat";
  notes?: string;
}

export interface ReportData {
  client: string;
  period: string;
  dataSource: "provided_report";
  kpis: ReportKPI[];
}

export interface Anomaly {
  id: string;
  metric: string;
  value: string;
  severity: "high" | "medium" | "low";
  interpretationStatus: InterpretationStatus;
  nextAction: string;
}

export interface ReactStep {
  step: number;
  reason: string;
  act: string;
  observe: string;
  nextDecision: string;
}

export interface OsintSource {
  id: string;
  source: string;
  type: "official" | "social" | "press" | "reviews" | "industry";
  freshness: string;
  quality: "high" | "medium" | "low";
  triangulation: number;
  confidenceScore: number;
  status: "VALIDATED" | "BLOCKED" | "WARNING";
  dataSource: CIDataSource;
}

export interface AMCDimension {
  level: "HIGH" | "MEDIUM" | "LOW";
  justification: string;
}

export interface AMCEntry {
  competitor: string;
  type: string;
  awareness: AMCDimension;
  motivation: AMCDimension;
  capability: AMCDimension;
  responseProbability: string;
  timeline: string;
}

export interface Scenario {
  id: string;
  quadrant: { x: "low" | "high"; y: "low" | "high" };
  xLabel: string;
  yLabel: string;
  title: string;
  dominant: boolean;
  signposts: string[];
  decision: string;
}

export interface ConfidenceBreakdown {
  component: string;
  weight: number;
  score: number;
  contribution: number;
}

export interface ConfidenceIndex {
  kpiReliability: number;
  osintConfidence: number;
  historicalCoverage: number;
  finalIndex: number;
  mode: "FULL" | "LIMITED" | "SILENCE";
  breakdown: ConfidenceBreakdown[];
  threshold: number;
}

export interface Claim {
  id: string;
  text: string;
  type: "causal" | "descriptive" | "predictive" | "comparative";
  source: string;
  status: "APPROVED" | "BLOCKED";
  reason: string;
}

export interface StrategyAction {
  text: string;
  owner: string;
  kpi: string;
  horizon: string;
}

export interface StrategyPlan {
  immediate: StrategyAction[];
  shortTerm: StrategyAction[];
  structural: StrategyAction[];
  dataSource: "precomputed_demo";
}

export interface CognitiveOutputData {
  status: "PREOCUPANTE" | "ESTABLE" | "POSITIVO";
  confidence: "FULL" | "LIMITADA" | "INSUFICIENTE";
  summary: string;
  keyFinding: string;
  mainUncertainty: string;
}

export interface DecisionOption {
  id: "A" | "B" | "C";
  title: string;
  description: string;
  selected: boolean;
}
