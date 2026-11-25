import type { AnalysisResult } from "./types";

export async function analyzeResume(file: File, jobDescription: string): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("file", file);
  form.append("job_description", jobDescription);

  const res = await fetch("/api/analyze", { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${res.status})`);
  }
  return res.json();
}
