import { useRef, useState, type DragEvent, type FormEvent } from "react";

interface Props {
  loading: boolean;
  onSubmit: (file: File, jobDescription: string) => void;
}

export default function UploadForm({ loading, onSubmit }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [jd, setJd] = useState("");
  const [dragging, setDragging] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (file) onSubmit(file, jd);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div
        role="button"
        tabIndex={0}
        onClick={() => input.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && input.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition ${
          dragging ? "border-accent bg-indigo-50" : "border-slate-300 bg-white hover:border-slate-400"
        }`}
      >
        <input
          ref={input}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        {file ? (
          <p className="font-medium">{file.name}</p>
        ) : (
          <>
            <p className="font-medium">Drop your resume PDF here</p>
            <p className="mt-1 text-sm text-slate-500">or click to browse. Max 5 MB.</p>
          </>
        )}
      </div>

      <div>
        <label htmlFor="jd" className="mb-1.5 block text-sm font-medium text-slate-700">
          Job description <span className="font-normal text-slate-400">(optional)</span>
        </label>
        <textarea
          id="jd"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          rows={8}
          placeholder="Paste the job posting to see which keywords you're missing."
          className="w-full rounded-xl border border-slate-300 bg-white p-3 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-indigo-100"
        />
      </div>

      <button
        type="submit"
        disabled={!file || loading}
        className="w-full rounded-xl bg-accent px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze resume"}
      </button>
    </form>
  );
}
