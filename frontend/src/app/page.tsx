'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import GraphVisualizer from '@/components/GraphVisualizer';
import AIChatAssistant from '@/components/AIChatAssistant';
import { Shield, Map, Share2, Search, Sparkles, UserCircle } from 'lucide-react';
import axios from 'axios';

// Dynamically import the map to prevent Next.js SSR "window is not defined" error
const IntelligenceMap = dynamic(() => import('@/components/IntelligenceMap'), { ssr: false });

const ROLES = ["Investigator", "Analyst", "Supervisor", "Policymaker"];

export default function Home() {
  const [role, setRole] = useState("Investigator");
  const [token, setToken] = useState("");

  // Fetch a token whenever the role changes
  useEffect(() => {
    const fetchToken = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await axios.post(`${API_URL}/api/v1/auth/token`, { role });
        const newToken = res.data.access_token;
        setToken(newToken);
        // Inject token globally for all Axios requests in child components
        axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      } catch (err) {
        console.error("Failed to fetch mock auth token", err);
      }
    };
    fetchToken();
  }, [role]);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 flex flex-col font-sans overflow-x-hidden">
      {/* Mock Auth Banner */}
      <div className="bg-yellow-500/20 text-yellow-500 px-4 py-1.5 text-xs text-center border-b border-yellow-500/50 font-medium">
        Mock Auth Mode: Role switcher enabled for hackathon demonstration purposes. No real credentials required.
      </div>
      {/* Top Navbar */}
      <header className="min-h-16 h-auto border-b border-slate-800 bg-slate-900/50 flex flex-wrap items-center px-4 lg:px-6 py-3 lg:py-0 justify-between backdrop-blur gap-4 lg:gap-0 sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <Shield className="text-red-500 w-6 h-6 lg:w-7 lg:h-7" />
          <h1 className="text-lg lg:text-xl font-bold tracking-tight text-white hidden sm:block">K-Sight - Intelligence Engine</h1>
          <h1 className="text-lg font-bold tracking-tight text-white sm:hidden">K-Sight</h1>
        </div>
        <div className="flex items-center gap-3 lg:gap-4 w-full lg:w-auto justify-between lg:justify-end">
          <div className="relative flex items-center gap-2 lg:border-r lg:border-slate-700 lg:pr-4 flex-1 lg:flex-none">
            <UserCircle className="text-slate-400 hidden sm:block" size={20} />
            <span className="text-sm text-slate-400 font-medium hidden sm:block">Role:</span>
            <select 
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-md px-3 py-1.5 lg:px-2 lg:py-1 text-sm text-white focus:outline-none focus:ring-1 focus:ring-red-500 w-full lg:w-auto"
            >
              {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          
        </div>
      </header>

      {/* Main Layout (Responsive 3-Column Grid) */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 p-4 lg:p-6 gap-4 lg:gap-6 lg:h-[calc(100vh-4rem)] lg:overflow-hidden h-auto">
        
        {/* Geographic Map Section (Left: 4/12) */}
        <section className="lg:col-span-4 flex flex-col gap-3 lg:gap-4 relative min-h-[400px] lg:min-h-0">
          <div className="flex items-center gap-2">
            <Map className="text-blue-400" size={20} />
            <h2 className="text-base lg:text-lg font-semibold text-white">Live Operations Map</h2>
          </div>
          <div className="flex-1 w-full rounded-xl relative z-0 border border-slate-700/50 shadow-lg">
             {token && <IntelligenceMap />}
          </div>
        </section>

        {/* Graph Investigation (Center: 5/12) */}
        <section className="lg:col-span-5 flex flex-col gap-3 lg:gap-4 relative min-h-[500px] lg:min-h-0">
          <div className="flex items-center gap-2">
            <Share2 className="text-emerald-400" size={20} />
            <h2 className="text-base lg:text-lg font-semibold text-white">Graph Investigator</h2>
          </div>
          <div className="flex-1 w-full rounded-xl relative z-0 border border-slate-700/50 shadow-lg">
            {token && <GraphVisualizer />}
          </div>
        </section>

        {/* AI Chat Assistant (Right: 3/12) */}
        <section className="lg:col-span-3 flex flex-col gap-3 lg:gap-4 relative min-h-[500px] lg:min-h-0">
          <div className="flex items-center gap-2">
            <Sparkles className="text-red-400" size={20} />
            <h2 className="text-base lg:text-lg font-semibold text-white">AI Agent</h2>
          </div>
          <div className="flex-1 w-full relative z-0 border border-slate-700/50 shadow-lg rounded-xl overflow-hidden">
            {token && <AIChatAssistant />}
          </div>
        </section>

      </div>
    </main>
  );
}
