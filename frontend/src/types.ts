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
  skills: string[];
  score: number;
}

export interface BulletFeedback {
  text: string;
  problems: string[];
}

export interface AnalysisResult {
  score: number;
  page_count: number;
  word_count: number;
  contact: { email: string | null; phone: string | null; linkedin: string | null };
  sections: string[];
  fonts: string[];
  issues: Issue[];
  keywords: KeywordMatch | null;
  bullets: BulletFeedback[];
  extracted_text: string;
  lines: TextLine[];
}

export interface TextLine {
  page: number;
  top: number;
  x0: number;
  text: string;
  scrambled: boolean;
  zone: "header" | "body" | "footer";
}
