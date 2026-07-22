'use client';
import { useState } from 'react';
import axios from 'axios';
import { Send, Bot, User, ShieldAlert } from 'lucide-react';

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

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:8000/api/v1/ai/ask', { query: userMsg });
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: res.data.answer,
        citations: res.data.citations,
        confidence: res.data.confidence
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Failed to reach Intelligence Engine.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-2xl">
      <div className="bg-slate-800 p-4 border-b border-slate-700 flex items-center gap-2">
        <Bot className="text-red-400" />
        <h3 className="text-white font-semibold">Gemini Intelligence</h3>
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
              <p className="whitespace-pre-wrap">{msg.content}</p>
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
        <div className="relative">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Query the platform..."
            className="w-full bg-slate-900 border border-slate-600 rounded-full pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 text-white placeholder-slate-400"
          />
          <button 
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-red-500 hover:bg-red-600 rounded-full text-white transition-colors disabled:opacity-50"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
