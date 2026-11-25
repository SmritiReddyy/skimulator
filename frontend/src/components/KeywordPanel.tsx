import type { KeywordMatch } from "../types";

function Chips({ words, className }: { words: string[]; className: string }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {words.map((w) => (
        <span key={w} className={`rounded-md px-2 py-0.5 font-mono text-xs ${className}`}>
          {w}
        </span>
      ))}
    </div>
  );
}

export default function KeywordPanel({ keywords }: { keywords: KeywordMatch }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="mb-2 text-sm font-semibold text-slate-700">In your resume ({keywords.matched.length})</h4>
        <Chips words={keywords.matched} className="bg-emerald-100 text-emerald-800" />
      </div>
      <div>
        <h4 className="mb-2 text-sm font-semibold text-slate-700">Missing ({keywords.missing.length})</h4>
        <Chips words={keywords.missing} className="bg-slate-200 text-slate-700" />
      </div>
    </div>
  );
}
