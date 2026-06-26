const items = [
  ["overall", "Overall"],
  ["technical", "Technical"],
  ["communication", "Communication"],
  ["confidence", "Confidence"],
];

export function ScoreStrip({ scores }) {
  if (!scores) return null;

  return (
    <section className="grid gap-3 sm:grid-cols-4">
      {items.map(([key, label]) => (
        <div key={key} className="rounded-lg border border-line bg-white p-4">
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-1 text-2xl font-semibold text-ink">{scores[key]}/100</p>
        </div>
      ))}
    </section>
  );
}
