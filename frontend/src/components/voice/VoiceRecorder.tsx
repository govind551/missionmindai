import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Play, Pause, RotateCcw } from 'lucide-react';
import { voiceService } from '../../services/api';

interface VoiceRecorderProps {
  onTranscribedText: (text: string) => void;
  lastAssistantAnswer?: string;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscribedText,
  lastAssistantAnswer
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [speechSpeed, setSpeechSpeed] = useState<number>(1.0);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check Web Speech API support
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          onTranscribedText(transcript);
        }
        setIsRecording(false);
      };

      recognition.onerror = (e: any) => {
        console.warn("Speech recognition error:", e);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    } else {
      setIsSpeechSupported(false);
    }

    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, [onTranscribedText]);

  const toggleRecording = () => {
    if (!recognitionRef.current) {
      // Fallback: trigger demo inquiry
      onTranscribedText("What went wrong with thermal control on past space probes?");
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsRecording(true);
      } catch (e) {
        console.warn("Could not start recognition:", e);
      }
    }
  };

  const handlePlayAnswer = () => {
    if (!lastAssistantAnswer) return;

    if (isPlaying) {
      window.speechSynthesis.pause();
      setIsPlaying(false);
    } else {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        setIsPlaying(true);
      } else {
        window.speechSynthesis.cancel();
        // Strip markdown asterisks and citations for natural voice
        const cleanText = lastAssistantAnswer
          .replace(/[#*`>]/g, '')
          .replace(/\[Doc:[^\]]+\]/g, '')
          .replace(/Page \d+/g, '');

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = speechSpeed;
        utterance.onend = () => setIsPlaying(false);
        utterance.onerror = () => setIsPlaying(false);

        window.speechSynthesis.speak(utterance);
        setIsPlaying(true);
      }
    }
  };

  const handleResetAudio = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    }
  };

  return (
    <div className="flex items-center space-x-2">
      {/* Microphone Record Button */}
      <button
        type="button"
        onClick={toggleRecording}
        className={`p-2.5 rounded-xl transition-all cursor-pointer ${
          isRecording
            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/50 animate-pulse'
            : 'bg-space-850 hover:bg-space-800 text-slate-400 hover:text-white border border-space-700'
        }`}
        title={isRecording ? "Listening... Click to stop" : "Speak query (Microphone)"}
      >
        {isRecording ? <MicOff className="w-4 h-4 text-rose-400" /> : <Mic className="w-4 h-4" />}
      </button>

      {/* Answer Playback Controls (if answer available) */}
      {lastAssistantAnswer && (
        <div className="flex items-center space-x-1 px-2 py-1 rounded-xl bg-space-850 border border-space-700 text-xs">
          <button
            type="button"
            onClick={handlePlayAnswer}
            className="p-1.5 rounded-lg text-cosmic-purple hover:text-white hover:bg-space-800 transition-colors"
            title={isPlaying ? "Pause voice output" : "Listen to answer"}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          </button>
          <button
            type="button"
            onClick={handleResetAudio}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-space-800 transition-colors"
            title="Reset audio"
          >
            <RotateCcw className="w-3 h-3" />
          </button>
          <select
            value={speechSpeed}
            onChange={(e) => setSpeechSpeed(parseFloat(e.target.value))}
            className="bg-transparent text-[10px] text-slate-400 font-mono focus:outline-none cursor-pointer"
            title="Speech Rate"
          >
            <option value="0.8" className="bg-space-900">0.8x</option>
            <option value="1.0" className="bg-space-900">1.0x</option>
            <option value="1.2" className="bg-space-900">1.2x</option>
          </select>
        </div>
      )}
    </div>
  );
};
