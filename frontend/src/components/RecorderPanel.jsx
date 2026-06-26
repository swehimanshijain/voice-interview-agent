import { Mic, Square, Waves } from "lucide-react";

export function RecorderPanel({
  transcript,
  interimTranscript,
  isListening,
  isSupported,
  error,
  onStart,
  onStop,
  isSubmitting,
}) {
  return (
    <section className="rounded-lg border border-line bg-white p-6 shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-accent">
            Live Transcript
          </p>
          <p className="mt-1 text-sm text-slate-500">
            {isSupported
              ? "Browser speech recognition is ready."
              : "Use Chrome or Edge for browser-native speech recognition."}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onStart}
            disabled={!isSupported || isListening || isSubmitting}
            className="inline-flex min-h-11 items-center gap-2 rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            <Mic size={18} />
            Start Recording
          </button>
          <button
            type="button"
            onClick={onStop}
            disabled={!isListening || isSubmitting}
            className="inline-flex h-11 w-11 items-center justify-center rounded-md border border-line text-ink hover:border-coral hover:text-coral disabled:cursor-not-allowed disabled:text-slate-400"
            aria-label="Stop recording"
            title="Stop recording"
          >
            <Square size={18} />
          </button>
        </div>
      </div>

      <div className="mt-5 min-h-40 rounded-md border border-line bg-panel p-4 text-base leading-7 text-slate-800">
        {transcript || interimTranscript ? (
          <>
            <span>{transcript}</span>
            {interimTranscript ? (
              <span className="text-slate-500"> {interimTranscript}</span>
            ) : null}
          </>
        ) : (
          <span className="text-slate-400">Your words will appear here while you speak.</span>
        )}
      </div>

      <div className="mt-4 flex min-h-6 items-center gap-2 text-sm">
        {isListening ? (
          <span className="inline-flex items-center gap-2 font-semibold text-accent">
            <Waves size={17} className="animate-pulse" />
            Listening...
          </span>
        ) : null}
        {isSubmitting ? <span className="font-semibold text-ink">Evaluating...</span> : null}
        {error ? <span className="text-coral">{error}</span> : null}
      </div>
    </section>
  );
}
