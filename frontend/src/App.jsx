import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, BrainCircuit } from "lucide-react";

import { FinalReport } from "./components/FinalReport";
import { InterviewTypeSelector } from "./components/InterviewTypeSelector";
import { QuestionPanel } from "./components/QuestionPanel";
import { RecorderPanel } from "./components/RecorderPanel";
import { ScoreStrip } from "./components/ScoreStrip";
import { useSpeechRecognition } from "./hooks/useSpeechRecognition";
import { useSpeechSynthesis } from "./hooks/useSpeechSynthesis";
import { completeSession, createSession, fetchInterviewTypes, submitAnswer } from "./services/api";

export default function App() {
  const [interviewTypes, setInterviewTypes] = useState([]);
  const [selectedType, setSelectedType] = useState("");
  const [session, setSession] = useState(null);
  const [report, setReport] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const speech = useSpeechRecognition();
  const tts = useSpeechSynthesis();

  const activeQuestionText = useMemo(() => {
    if (!session?.current_question) return "";
    return session.current_question.question;
  }, [session]);

  useEffect(() => {
    fetchInterviewTypes()
      .then((types) => {
        setInterviewTypes(types);
        setSelectedType(types[0]?.id || "");
      })
      .catch(() => {
        setError("Could not reach the backend. Start FastAPI on port 8000 and refresh.");
      });
  }, []);

  async function handleStart() {
    setIsStarting(true);
    setError("");
    setReport(null);
    speech.reset();

    try {
      const nextSession = await createSession(selectedType);
      setSession(nextSession);
      tts.speak(`${nextSession.greeting} ${nextSession.current_question.question}`);
    } catch (err) {
      setError(apiError(err));
    } finally {
      setIsStarting(false);
    }
  }

  function handleSpeakCurrent() {
    if (!session) return;
    const coaching = session.coaching_hint ? `${session.coaching_hint} ` : "";
    tts.speak(`${coaching}${activeQuestionText}`);
  }

  function handleStartRecording() {
    tts.stopSpeaking();
    setError("");
    speech.start();
  }

  async function handleStopRecording() {
    setIsSubmitting(true);
    setError("");
    const transcript = await speech.stop();

    if (!transcript) {
      setIsSubmitting(false);
      setError("I could not detect speech. Try recording again.");
      return;
    }

    try {
      const updated = await submitAnswer(session.session_id, transcript);
      setSession(updated);
      speech.reset();

      if (updated.status === "completed") {
        const finalResponse = await completeSession(updated.session_id);
        setReport(finalResponse.report);
        tts.speak("Your interview is complete. I have prepared your final performance report.");
      } else if (updated.status === "coaching") {
        tts.speak(`${updated.coaching_hint} Here is your next question. ${updated.current_question.question}`);
      } else {
        tts.speak(updated.current_question.question);
      }
    } catch (err) {
      setError(apiError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleRestart() {
    tts.stopSpeaking();
    speech.reset();
    setSession(null);
    setReport(null);
    setError("");
  }

  const showInterview = session && !report;

  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-5">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-md bg-teal-50 text-accent">
              <BrainCircuit size={24} />
            </span>
            <div>
              <h1 className="text-xl font-semibold text-ink">AI Voice Interview Coach</h1>
              <p className="text-sm text-slate-500">Adaptive voice mock interviews with real-time evaluation</p>
            </div>
          </div>
          {session ? (
            <div className="text-right text-sm text-slate-500">
              <p className="font-semibold text-ink">
                Question {session.question_number} / {session.max_questions}
              </p>
              <p>{session.current_question?.topic_name || "Complete"}</p>
            </div>
          ) : null}
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-5 py-8">
        {error ? (
          <div className="mb-5 flex items-center gap-3 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-coral">
            <AlertTriangle size={18} />
            {error}
          </div>
        ) : null}

        {!session && !report ? (
          <InterviewTypeSelector
            interviewTypes={interviewTypes}
            selectedType={selectedType}
            onSelect={setSelectedType}
            onStart={handleStart}
            isLoading={isStarting}
          />
        ) : null}

        {showInterview ? (
          <div className="space-y-5">
            <QuestionPanel
              question={session.current_question}
              greeting={session.greeting}
              coachingHint={session.coaching_hint}
              onSpeak={handleSpeakCurrent}
              isSpeaking={tts.isSpeaking}
            />
            <RecorderPanel
              transcript={speech.transcript}
              interimTranscript={speech.interimTranscript}
              isListening={speech.isListening}
              isSupported={speech.isSupported}
              error={speech.error}
              onStart={handleStartRecording}
              onStop={handleStopRecording}
              isSubmitting={isSubmitting}
            />
            <ScoreStrip scores={session.scores} />
            {session.latest_evaluation ? (
              <section className="rounded-lg border border-line bg-white p-5">
                <p className="font-semibold text-ink">Latest Feedback</p>
                <p className="mt-2 text-sm leading-6 text-slate-700">
                  {session.latest_evaluation.feedback}
                </p>
              </section>
            ) : null}
          </div>
        ) : null}

        {report ? <FinalReport report={report} onRestart={handleRestart} /> : null}
      </div>
    </main>
  );
}

function apiError(err) {
  return err?.response?.data?.detail || err.message || "Something went wrong.";
}
