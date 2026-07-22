import IntelligenceMap from '@/components/IntelligenceMap';
import GraphVisualizer from '@/components/GraphVisualizer';
import AIChatAssistant from '@/components/AIChatAssistant';
import { Shield, Map, Share2, Search, Sparkles } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/50 flex items-center px-6 justify-between backdrop-blur">
        <div className="flex items-center gap-3">
          <Shield className="text-red-500" size={28} />
          <h1 className="text-xl font-bold tracking-tight text-white">Intelligence Engine</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Ask AI: Show robbery hotspots..."
              className="bg-slate-800 border border-slate-700 rounded-full pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 w-80 text-white"
            />
          </div>
          <div className="h-8 w-8 rounded-full bg-slate-700 border border-slate-600"></div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex p-6 gap-6 h-[calc(100vh-4rem)]">
        
        {/* Geographic Map Section (Left) */}
        <section className="flex-[1.5] flex flex-col gap-4 relative">
          <div className="flex items-center gap-2">
            <Map className="text-blue-400" size={20} />
            <h2 className="text-lg font-semibold text-white">Live Operations Map</h2>
          </div>
          <div className="flex-1 w-full rounded-xl relative z-0">
             <IntelligenceMap />
          </div>
        </section>

        {/* Right Column (Graph + Chat) */}
        <section className="flex-1 flex flex-col gap-6">
          
          {/* Graph Investigation */}
          <div className="flex-1 flex flex-col gap-4 relative">
            <div className="flex items-center gap-2">
              <Share2 className="text-emerald-400" size={20} />
              <h2 className="text-lg font-semibold text-white">Graph Investigator</h2>
            </div>
            <div className="flex-1 w-full rounded-xl relative z-0">
              <GraphVisualizer />
            </div>
          </div>

          {/* AI Chat Assistant */}
          <div className="flex-1 flex flex-col gap-4 relative">
            <div className="flex items-center gap-2">
              <Sparkles className="text-red-400" size={20} />
              <h2 className="text-lg font-semibold text-white">AI Intelligence Agent</h2>
            </div>
            <div className="flex-1 w-full relative z-0">
              <AIChatAssistant />
            </div>
          </div>

        </section>

      </div>
    </main>
  );
}
