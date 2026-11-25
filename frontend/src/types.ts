export type Severity = "critical" | "warning" | "info";

export interface Issue {
  id: string;
  severity: Severity;
  title: string;
  detail: string;
}

export interface KeywordMatch {
  matched: string[];
  missing: string[];
  score: number;
}

export interface AnalysisResult {
  score: number;
  page_count: number;
  word_count: number;
  contact: { email: string | null; phone: string | null; linkedin: string | null };
  sections: string[];
  issues: Issue[];
  keywords: KeywordMatch | null;
  extracted_text: string;
}
