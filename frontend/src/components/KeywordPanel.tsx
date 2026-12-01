import type { KeywordMatch } from "../types";

function Chip({ word, found }: { word: string; found: boolean }) {
  return (
    <span
      className={`rounded-md px-2 py-0.5 font-mono text-xs ${
        found
          ? "bg-emerald-100 text-emerald-800"
          : "border border-dashed border-rose-300 bg-rose-50 text-rose-700"
      }`}
      title={found ? "Found in your resume" : "Missing from your resume"}
    >
      {word}
    </span>
  );
}

function Group({ title, terms, matched }: { title: string; terms: string[]; matched: Set<string> }) {
  if (terms.length === 0) return null;
  const hits = terms.filter((t) => matched.has(t)).length;
  // Missing terms first: they're what the user needs to act on.
  const sorted = [...terms].sort((a, b) => Number(matched.has(a)) - Number(matched.has(b)));

  return (
    <div>
      <h4 className="mb-2 text-sm font-semibold text-slate-700">
        {title}{" "}
        <span className="font-normal text-slate-400">
          {hits}/{terms.length} found
        </span>
      </h4>
      <div className="flex flex-wrap gap-1.5">
        {sorted.map((t) => (
          <Chip key={t} word={t} found={matched.has(t)} />
        ))}
      </div>
    </div>
  );
}

export default function KeywordPanel({ keywords }: { keywords: KeywordMatch }) {
  const matched = new Set(keywords.matched);
  const skills = new Set(keywords.skills);
  const all = [...keywords.matched, ...keywords.missing];

  return (
    <div className="space-y-5">
      <Group title="Skills" terms={all.filter((t) => skills.has(t))} matched={matched} />
      <Group title="Other terms" terms={all.filter((t) => !skills.has(t))} matched={matched} />
      <p className="text-xs text-slate-400">
        Skills count double towards the keyword score. Synonyms like k8s / Kubernetes are matched
        automatically.
      </p>
    </div>
  );
}
