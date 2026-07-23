import { useState, useEffect } from 'react';
import axios from 'axios';
import { FileText, Loader2 } from 'lucide-react';

interface SimilarCase {
  fir_id: string;
  type: string;
  location: string;
  date: string;
  score: number;
}

export default function SimilarCasesPanel({ firId }: { firId: string }) {
  const [cases, setCases] = useState<SimilarCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    const fetchSimilar = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await axios.get(`${API_URL}/api/v1/intelligence/similar/${firId}`);
        setCases(res.data);
      } catch (err) {
        setError('Failed to load similar cases.');
      } finally {
        setLoading(false);
      }
    };
    fetchSimilar();
  }, [firId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-4">
        <Loader2 className="animate-spin text-slate-400 mb-2" size={20} />
        <span className="text-xs text-slate-400">Finding similar cases...</span>
      </div>
    );
  }

  if (error) {
    return <div className="text-xs text-red-400 p-2">{error}</div>;
  }

  if (cases.length === 0) {
    return <div className="text-xs text-slate-400 p-2">No similar past cases found.</div>;
  }

  return (
    <div className="flex flex-col gap-3">
      <h4 className="text-sm font-semibold flex items-center gap-1.5 text-slate-200">
        <FileText size={16} className="text-blue-400" />
        Similar Past Cases
      </h4>
      <div className="flex flex-col gap-2">
        {cases.map((c, i) => (
          <div key={i} className="bg-slate-900 border border-slate-700 rounded p-2.5 flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-300">{c.fir_id}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-900/50 text-blue-300 border border-blue-800">
                {c.score}% Match
              </span>
            </div>
            <span className="text-[11px] text-slate-400 truncate">{c.location} • {c.date.split('T')[0]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
