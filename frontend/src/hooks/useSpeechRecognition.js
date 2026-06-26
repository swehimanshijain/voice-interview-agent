import { useCallback, useMemo, useRef, useState } from "react";

export function useSpeechRecognition() {
  const SpeechRecognition = useMemo(
    () => window.SpeechRecognition || window.webkitSpeechRecognition,
    [],
  );
  const recognitionRef = useRef(null);
  const finalTranscriptRef = useRef("");
  const interimTranscriptRef = useRef("");
  const combinedTranscriptRef = useRef("");
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState("");

  const isSupported = Boolean(SpeechRecognition);

  const start = useCallback(() => {
    if (!SpeechRecognition) {
      setError("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    finalTranscriptRef.current = "";
    interimTranscriptRef.current = "";
    combinedTranscriptRef.current = "";
    setTranscript("");
    setInterimTranscript("");
    setError("");

    recognition.onresult = (event) => {
      let interim = "";
      let finalText = finalTranscriptRef.current;

      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const chunk = event.results[index][0].transcript;
        if (event.results[index].isFinal) {
          finalText = `${finalText} ${chunk}`.trim();
        } else {
          interim = `${interim} ${chunk}`.trim();
        }
      }

      finalTranscriptRef.current = finalText;
      interimTranscriptRef.current = interim;
      combinedTranscriptRef.current = `${finalText} ${interim}`.trim();
      setTranscript(finalText);
      setInterimTranscript(interim);
    };

    recognition.onerror = (event) => {
      setError(event.error || "Speech recognition failed.");
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  }, [SpeechRecognition]);

  const stop = useCallback(
    () =>
      new Promise((resolve) => {
        const currentTranscript = () =>
          (combinedTranscriptRef.current || finalTranscriptRef.current || interimTranscriptRef.current).trim();

        const recognition = recognitionRef.current;
        if (!recognition) {
          resolve(currentTranscript());
          return;
        }

        recognition.onend = () => {
          setIsListening(false);
          setInterimTranscript("");
          recognitionRef.current = null;
          resolve(currentTranscript());
        };

        try {
          recognition.stop();
        } catch {
          setIsListening(false);
          recognitionRef.current = null;
          resolve(currentTranscript());
        }
      }),
    [],
  );

  const reset = useCallback(() => {
    finalTranscriptRef.current = "";
    interimTranscriptRef.current = "";
    combinedTranscriptRef.current = "";
    setTranscript("");
    setInterimTranscript("");
    setError("");
  }, []);

  return {
    transcript,
    interimTranscript,
    isListening,
    isSupported,
    error,
    start,
    stop,
    reset,
  };
}
