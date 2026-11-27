import { useState, type ReactNode } from "react";
import { analyzeResume } from "./api";
import ExtractedText from "./components/ExtractedText";
import IssueList from "./components/IssueList";
import KeywordPanel from "./components/KeywordPanel";
import ScoreRing from "./components/ScoreRing";
import UploadForm from "./components/UploadForm";
import type { AnalysisResult } from "./types";

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      {children}
    </section>
  );
}

export default function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(file: File, jd: string) {
    setLoading(true);
    setError(null);
    try {
      setResult(await analyzeResume(file, jd));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <header className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight">
          Skim<span className="text-accent">ulator</span>
        </h1>
        <p className="mt-2 text-slate-600">
          See your resume the way an applicant tracking system does, so it doesn't get filtered out before a
          recruiter ever reads it.
        </p>
      </header>

      <div className="grid gap-8 lg:grid-cols-[380px_1fr]">
        <aside>
          <UploadForm loading={loading} onSubmit={handleSubmit} />
          {error && <p className="mt-4 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
        </aside>

        <main className="space-y-6">
          {!result ? (
            <div className="flex h-full min-h-64 items-center justify-center rounded-2xl border border-dashed border-slate-300 text-slate-400">
              Results will appear here
            </div>
          ) : (
            <>
              <section className="flex flex-wrap items-center justify-around gap-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <ScoreRing score={result.score} label="ATS compatibility" />
                {result.keywords && <ScoreRing score={result.keywords.score} label="Keyword match" />}
                <dl className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
                  <dt className="text-slate-500">Pages</dt>
                  <dd className="font-medium">{result.page_count}</dd>
                  <dt className="text-slate-500">Words</dt>
                  <dd className="font-medium">{result.word_count}</dd>
                  <dt className="text-slate-500">Sections</dt>
                  <dd className="font-medium capitalize">{result.sections.join(", ") || "none"}</dd>
                  <dt className="text-slate-500">Email</dt>
                  <dd className="font-medium">{result.contact.email ?? "not found"}</dd>
                </dl>
              </section>

              <Card title="Issues">
                <IssueList issues={result.issues} />
              </Card>

              {result.keywords && (
                <Card title="Job description keywords">
                  <KeywordPanel keywords={result.keywords} />
                </Card>
              )}

              <Card title="What the ATS sees">
                <ExtractedText lines={result.lines} fallback={result.extracted_text} />
              </Card>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
