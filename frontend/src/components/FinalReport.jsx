import { Award, CheckCircle2, Target } from "lucide-react";

export function FinalReport({ report, onRestart }) {
  if (!report) return null;

  return (
    <section className="mx-auto max-w-5xl rounded-lg border border-line bg-white p-6 shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-accent">Final Report</p>
          <h2 className="mt-2 text-3xl font-semibold text-ink">
            Overall Score: {report.overall_score}/100
          </h2>
        </div>
        <button
          type="button"
          onClick={onRestart}
          className="rounded-md bg-ink px-4 py-3 font-semibold text-white hover:bg-slate-800"
        >
          New Interview
        </button>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        <Metric label="Technical" value={report.technical_score} />
        <Metric label="Communication" value={report.communication_score} />
        <Metric label="Confidence" value={report.confidence_score} />
      </div>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <ListBlock icon={CheckCircle2} title="Strengths" items={report.strengths} />
        <ListBlock icon={Target} title="Areas To Improve" items={report.areas_to_improve} />
      </div>

      <div className="mt-6 rounded-md bg-panel p-5">
        <p className="flex items-center gap-2 font-semibold text-ink">
          <Award size={18} />
          Personalized Feedback
        </p>
        <p className="mt-3 leading-7 text-slate-700">{report.personalized_feedback}</p>
        <p className="mt-4 leading-7 text-slate-700">{report.interview_summary}</p>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-line p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-ink">{value}/100</p>
    </div>
  );
}

function ListBlock({ icon: Icon, title, items }) {
  return (
    <div className="rounded-lg border border-line p-5">
      <p className="flex items-center gap-2 font-semibold text-ink">
        <Icon size={18} />
        {title}
      </p>
      <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
