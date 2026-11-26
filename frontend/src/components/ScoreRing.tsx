interface Props {
  score: number;
  label: string;
  size?: number;
}

function colorFor(score: number) {
  if (score >= 85) return "text-emerald-500";
  if (score >= 60) return "text-amber-500";
  return "text-rose-500";
}

export default function ScoreRing({ score, label, size = 120 }: Props) {
  const stroke = 10;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            strokeWidth={stroke}
            className="fill-none stroke-slate-200"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={c}
            strokeDashoffset={offset}
            className={`fill-none stroke-current transition-[stroke-dashoffset] duration-700 ${colorFor(score)}`}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-3xl font-bold tabular-nums">
          {score}
        </span>
      </div>
      <span className="text-sm font-medium text-slate-500">{label}</span>
    </div>
  );
}
