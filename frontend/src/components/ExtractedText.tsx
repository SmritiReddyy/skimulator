import type { TextLine } from "../types";

interface Props {
  lines: TextLine[];
  fallback: string;
}

export default function ExtractedText({ lines, fallback }: Props) {
  if (lines.length === 0) {
    return (
      <pre className="max-h-96 overflow-auto rounded-xl bg-slate-50 p-4 font-mono text-xs whitespace-pre-wrap text-slate-700">
        {fallback || "(no text extracted)"}
      </pre>
    );
  }

  const scrambled = lines.filter((l) => l.scrambled).length;

  return (
    <div className="space-y-3">
      {scrambled > 0 && (
        <p className="flex items-center gap-2 text-sm text-amber-800">
          <span className="inline-block h-3 w-3 rounded-sm border-l-4 border-amber-500 bg-amber-100" />
          {scrambled} highlighted line{scrambled === 1 ? "" : "s"} mix text from two columns. This is how a
          parser reading left to right sees them.
        </p>
      )}
      <div className="max-h-96 overflow-auto rounded-xl bg-slate-50 p-4 font-mono text-xs leading-relaxed text-slate-700">
        {lines.map((line, i) => (
          <div key={i}>
            {i > 0 && line.page !== lines[i - 1].page && (
              <div className="my-3 border-t border-dashed border-slate-300 pt-1 text-[10px] text-slate-400 uppercase">
                Page {line.page}
              </div>
            )}
            <div
              className={
                line.scrambled ? "-mx-2 border-l-4 border-amber-500 bg-amber-100 px-1.5 text-amber-900" : ""
              }
            >
              {line.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
