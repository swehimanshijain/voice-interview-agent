import { Lightbulb, MessageSquareText, Volume2 } from "lucide-react";

export function QuestionPanel({ question, greeting, coachingHint, onSpeak, isSpeaking }) {
  return (
    <section className="rounded-lg border border-line bg-white p-6 shadow-soft">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-accent">
            {question?.kind === "follow_up" ? "Follow-up" : "Current Question"}
          </p>
          <h2 className="mt-2 text-xl font-semibold leading-8 text-ink">
            {question?.question || greeting}
          </h2>
          {question?.topic_name ? (
            <p className="mt-3 text-sm text-slate-500">{question.topic_name}</p>
          ) : null}
        </div>
        <button
          type="button"
          onClick={onSpeak}
          className="inline-flex h-11 w-11 items-center justify-center rounded-md border border-line text-ink hover:border-accent hover:text-accent"
          aria-label="Speak question"
          title="Speak question"
        >
          <Volume2 size={20} className={isSpeaking ? "animate-pulse" : ""} />
        </button>
      </div>

      {coachingHint ? (
        <div className="mt-5 rounded-md border border-amber-200 bg-amber-50 p-4">
          <p className="flex items-center gap-2 text-sm font-semibold text-coral">
            <Lightbulb size={17} />
            Coaching Hint
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-700">{coachingHint}</p>
        </div>
      ) : null}

      <div className="mt-5 flex items-center gap-2 text-sm text-slate-500">
        <MessageSquareText size={17} />
        Answer naturally. Stop recording submits automatically.
      </div>
    </section>
  );
}
