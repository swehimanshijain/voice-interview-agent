import { BriefcaseBusiness, Code2, Play } from "lucide-react";

const icons = {
  hr: BriefcaseBusiness,
  technical_sde: Code2,
};

export function InterviewTypeSelector({
  interviewTypes,
  selectedType,
  onSelect,
  onStart,
  isLoading,
}) {
  return (
    <section className="mx-auto grid w-full max-w-5xl gap-5 md:grid-cols-2">
      {interviewTypes.map((type) => {
        const Icon = icons[type.id] || BriefcaseBusiness;
        const active = selectedType === type.id;
        return (
          <button
            key={type.id}
            type="button"
            onClick={() => onSelect(type.id)}
            className={`min-h-56 rounded-lg border bg-white p-6 text-left shadow-soft transition ${
              active ? "border-accent ring-4 ring-teal-100" : "border-line hover:border-accent"
            }`}
          >
            <span className="mb-5 flex h-12 w-12 items-center justify-center rounded-md bg-teal-50 text-accent">
              <Icon size={26} />
            </span>
            <h2 className="text-2xl font-semibold text-ink">{type.label}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">{type.description}</p>
          </button>
        );
      })}

      <div className="md:col-span-2">
        <button
          type="button"
          onClick={onStart}
          disabled={!selectedType || isLoading}
          className="inline-flex min-h-12 items-center gap-2 rounded-md bg-ink px-5 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          <Play size={18} />
          {isLoading ? "Starting..." : "Start Interview"}
        </button>
      </div>
    </section>
  );
}
