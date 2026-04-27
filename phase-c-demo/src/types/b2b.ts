export type DataSource =
  | "precomputed_demo"
  | "real_pipeline_output"
  | "provided_report"
  | "simulated_realistic";

export interface PhaseCounts {
  scraped: number;
  enriched: number;
  validEmail: number;
  noEmail: number;
  discarded: number;
  dataSource: DataSource;
}

export interface CompanyRecord {
  id: string;
  name: string;
  domain: string;
  city: string;
  sector: string;
  size: "micro" | "pequeña" | "mediana" | "grande";
  email: string | null;
  status: "valid" | "no_email" | "discarded";
}

export interface ClusterProfile {
  cluster_id: number;
  label: string;
  tone: string;
  primary_sector: string;
  avg_size: string;
  avg_score: number;
  company_count: number;
  key_pain: string;
  value_prop: string;
  unclassifiable?: boolean;
  dataSource: DataSource;
}

export interface ClassifiedCompany {
  id: string;
  name: string;
  cluster_id: number;
  sector_confidence: number;
  lead_score: number;
}

export interface EmailDraft {
  id: string;
  recipient: string;
  recipient_company: string;
  subject: string;
  before_humanizer: string;
  after_humanizer: string;
  diff_segments: Array<{ text: string; changed: boolean }>;
  sequence_step: 0 | 1 | 2 | 3;
  cluster_id: number;
  tone: string;
  dataSource: DataSource;
}

export interface CampaignKPIs {
  campaign: string;
  open_rate: number;
  reply_rate: number;
  meeting_rate: number;
  open_lower_wilson: number;
  reply_lower_wilson: number;
}

export interface LearningInsight {
  id: string;
  text: string;
  confidence: number;
  references_wilson: boolean;
}

export interface AgentLog {
  ts: string;
  agent: string;
  action: string;
  result: string;
  confidence?: number;
  phase: 1 | 2 | 3 | 4;
}
