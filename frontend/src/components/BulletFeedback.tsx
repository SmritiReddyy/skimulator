import type { BulletFeedback as Bullet } from "../types";

const LABELS: Record<string, { text: string; className: string }> = {
  "no-metric": { text: "No numbers", className: "bg-sky-100 text-sky-700" },
  "weak-opener": { text: "Weak opener", className: "bg-amber-100 text-amber-700" },
  "too-long": { text: "Too long", className: "bg-violet-100 text-violet-700" },
};

export default function BulletFeedback({ bullets }: { bullets: Bullet[] }) {
  const flagged = bullets.filter((b) => b.problems.length > 0);
  const strong = bullets.length - flagged.length;

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-600">
        <span className="font-semibold text-emerald-600">{strong}</span> of {bullets.length} bullet
        {bullets.length === 1 ? "" : "s"} look strong.
        {flagged.length > 0 && " The rest could be sharper:"}
      </p>
      {flagged.length > 0 && (
        <ul className="space-y-2">
          {flagged.map((b, i) => (
            <li key={i} className="rounded-xl border border-slate-200 p-3">
              <p className="text-sm text-slate-800">{b.text}</p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {b.problems.map((p) => (
                  <span
                    key={p}
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${LABELS[p]?.className ?? "bg-slate-100"}`}
                  >
                    {LABELS[p]?.text ?? p}
                  </span>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
