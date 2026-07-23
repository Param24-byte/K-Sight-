'use client';
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, ShieldAlert, Mic, MicOff, Globe } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  confidence?: number;
}

export default function AIChatAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'I am your Intelligence Assistant. How can I help with the investigation today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<'English' | 'Kannada'>('English');
  const [isListening, setIsListening] = useState(false);
  
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Initialize Web Speech API for recognition
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        
        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInput(transcript);
          setIsListening(false);
        };
        
        recognitionRef.current.onerror = () => {
          setIsListening(false);
        };
        
        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
    }
  }, []);

  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = language === 'Kannada' ? 'kn-IN' : 'en-US';
    }
  }, [language]);

  const toggleListen = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  const speakResponse = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === 'Kannada' ? 'kn-IN' : 'en-US';
      // Attempt to find a native voice if possible
      const voices = window.speechSynthesis.getVoices();
      const preferredVoice = voices.find(v => v.lang.includes(language === 'Kannada' ? 'kn' : 'en'));
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      window.speechSynthesis.speak(utterance);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await axios.post(`${API_URL}/api/v1/ai/ask`, { 
        query: userMsg,
        language: language,
        history: messages.map(m => ({ role: m.role, content: m.content }))
      });
      
      const assistantReply = res.data.answer;
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: assistantReply,
        citations: res.data.citations,
        confidence: res.data.confidence
      }]);
      
      // Read out the response
      speakResponse(assistantReply);
      
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Failed to reach Intelligence Engine.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-2xl">
      <div className="bg-slate-800 p-4 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="text-red-400" />
          <h3 className="text-white font-semibold">Gemini Voice Intelligence</h3>
        </div>
        <div className="flex items-center gap-2 bg-slate-900 rounded-lg p-1 border border-slate-700">
          <Globe size={14} className="text-slate-400 ml-1" />
          <button 
            onClick={() => setLanguage('English')}
            className={`px-2 py-1 text-xs rounded-md font-medium transition-colors ${language === 'English' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            EN
          </button>
          <button 
            onClick={() => setLanguage('Kannada')}
            className={`px-2 py-1 text-xs rounded-md font-medium transition-colors ${language === 'Kannada' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            ಕನ್ನಡ
          </button>
        </div>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-red-900/50 flex items-center justify-center shrink-0 border border-red-800">
                <ShieldAlert size={16} className="text-red-400" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-lg p-3 text-sm ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-slate-800 text-slate-200 border border-slate-700'
            }`}>
              <p className="whitespace-pre-wrap leading-relaxed font-medium">{msg.content}</p>
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-700 text-xs text-slate-400">
                  <strong>Evidence Citations:</strong> {msg.citations.join(', ')}
                </div>
              )}
              {msg.confidence && (
                <div className="mt-1 text-xs text-emerald-400">
                  Confidence Score: {(msg.confidence * 100).toFixed(1)}%
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-blue-900/50 flex items-center justify-center shrink-0 border border-blue-800">
                <User size={16} className="text-blue-400" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start gap-3">
            <div className="w-8 h-8 rounded-full bg-red-900/50 flex items-center justify-center shrink-0 border border-red-800">
              <ShieldAlert size={16} className="text-red-400" />
            </div>
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 text-sm text-slate-400">
              Analyzing Knowledge Graph...
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-slate-800 border-t border-slate-700">
        <div className="relative flex gap-2">
          <button
            onClick={toggleListen}
            className={`p-3 rounded-full flex-shrink-0 transition-colors ${
              isListening 
                ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.5)]' 
                : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
            }`}
            title={isListening ? "Listening..." : "Tap to speak"}
          >
            {isListening ? <Mic size={20} /> : <MicOff size={20} />}
          </button>
          
          <div className="relative flex-1">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder={language === 'Kannada' ? "ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ..." : "Query the platform..."}
              className="w-full bg-slate-900 border border-slate-600 rounded-full pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-slate-400 font-medium"
            />
            <button 
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 hover:bg-blue-700 rounded-full text-white transition-colors disabled:opacity-50"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
