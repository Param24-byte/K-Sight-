'use client';
import { useState } from 'react';
import ReactFlow, { 
  Background, 
  useNodesState, 
  useEdgesState,
  Node,
  Edge,
  Position,
  ReactFlowProvider,
  useReactFlow,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';
import dagre from 'dagre';
import { Search, Loader2, X, ZoomIn, ZoomOut, Maximize } from 'lucide-react';
import SimilarCasesPanel from './SimilarCasesPanel';

const CustomZoomControls = () => {
  const { zoomIn, zoomOut, fitView } = useReactFlow();
  
  return (
    <Panel position="bottom-left" className="flex flex-col gap-2 bg-slate-800/90 p-2 rounded-lg border border-slate-700 shadow-xl backdrop-blur-sm mb-16 ml-2">
      <button onClick={() => zoomIn()} className="p-2 bg-slate-700 hover:bg-slate-600 rounded text-slate-200 hover:text-white transition-colors" title="Zoom In">
        <ZoomIn size={18} />
      </button>
      <button onClick={() => zoomOut()} className="p-2 bg-slate-700 hover:bg-slate-600 rounded text-slate-200 hover:text-white transition-colors" title="Zoom Out">
        <ZoomOut size={18} />
      </button>
      <button onClick={() => fitView({ duration: 800 })} className="p-2 bg-slate-700 hover:bg-slate-600 rounded text-slate-200 hover:text-white transition-colors" title="Fit View">
        <Maximize size={18} />
      </button>
    </Panel>
  );
};

// Helper to calculate the tree layout
const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  const nodeWidth = 172;
  const nodeHeight = 45;
  dagreGraph.setGraph({ rankdir: direction, nodesep: 50, edgesep: 30, ranksep: 80 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    const newNode = { ...node };

    newNode.targetPosition = direction === 'LR' ? Position.Left : Position.Top;
    newNode.sourcePosition = direction === 'LR' ? Position.Right : Position.Bottom;

    newNode.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };

    return newNode;
  });

  return { nodes: newNodes, edges };
};

export default function GraphVisualizer() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setSelectedNode(null);
    
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await axios.get(`${API_URL}/api/v1/graph/case/${searchQuery}`);
      
      if (res.data && res.data.nodes) {
        const rawNodes: Node[] = res.data.nodes.map((n: any) => ({
          id: n.id,
          type: n.type,
          position: { x: 0, y: 0 },
          data: { 
            label: n.type === 'incident' ? `FIR: ${n.label}` : n.label, 
            details: n.details, 
            type: n.type,
            risk_score: n.risk_score 
          },
          style: { 
            background: n.type === 'incident' ? '#b91c1c' : n.type === 'accused' ? (n.risk_score > 60 ? '#ef4444' : n.risk_score >= 30 ? '#f59e0b' : '#10b981') : n.type === 'complainant' ? '#10b981' : n.type === 'victim' ? '#f59e0b' : '#8b5cf6',
            color: 'white',
            border: n.type === 'incident' ? '2px solid #f87171' : '1px solid rgba(255,255,255,0.2)',
            borderRadius: n.type === 'incident' ? '4px' : '8px',
            padding: '10px',
            fontSize: '12px',
            fontWeight: 'bold',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)'
          }
        }));

        const rawEdges: Edge[] = res.data.edges.map((e: any, idx: number) => ({
          id: `e${idx}`,
          source: e.source,
          target: e.target,
          label: e.label,
          animated: true,
          style: { stroke: '#94a3b8', strokeWidth: 1.5 },
          labelStyle: { fill: '#94a3b8', fontWeight: 700, fontSize: 10 },
          labelBgStyle: { fill: '#1e293b' }
        }));

        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          rawNodes,
          rawEdges,
          'TB'
        );

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
      }
    } catch (err) {
      console.error("Graph Data Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full w-full rounded-xl overflow-hidden border border-slate-700 bg-slate-900 shadow-2xl relative flex flex-col">
      <div className="p-3 bg-slate-800/80 backdrop-blur border-b border-slate-700 z-10 flex gap-2">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input 
              type="text" 
              placeholder="Enter Crime No (e.g. 100010001202600000)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-md py-1.5 pl-9 pr-3 text-sm text-white focus:outline-none focus:border-red-500"
            />
          </div>
          <button type="submit" disabled={loading} className="bg-red-500 hover:bg-red-600 text-white px-4 py-1.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50">
            {loading ? <Loader2 className="animate-spin" size={16} /> : "Explore Case"}
          </button>
        </form>
      </div>
      
      <div className="flex-1 relative">
        {nodes.length === 0 && !loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-sm">
            Enter an FIR ID to explore its case graph
          </div>
        ) : (
          <ReactFlowProvider>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={(e, node) => setSelectedNode(node)}
              fitView
              attributionPosition="bottom-right"
            >
              <Background color="#475569" gap={20} size={1.5} />
              <CustomZoomControls />
            </ReactFlow>
          </ReactFlowProvider>
        )}

        {selectedNode && (
          <div className="absolute top-4 right-4 w-72 bg-slate-800/95 backdrop-blur-md border border-slate-700 rounded-xl shadow-2xl z-20 flex flex-col max-h-[calc(100%-2rem)]">
            <div className="flex items-center justify-between p-3 border-b border-slate-700">
              <h3 className="font-semibold text-white truncate pr-2 text-sm uppercase">
                {selectedNode.data.type}: {selectedNode.data.label}
              </h3>
              <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-white">
                <X size={16} />
              </button>
            </div>
            <div className="p-4 overflow-y-auto flex flex-col gap-3 text-sm">
              <p className="text-slate-300"><span className="text-slate-500 font-medium">ID:</span> {selectedNode.id}</p>
              {selectedNode.data.details && Object.entries(selectedNode.data.details).map(([k, v]) => (
                <div key={k} className="flex flex-col">
                  <span className="text-xs text-slate-400">{k}</span>
                  <span className="text-sm font-medium">{String(v)}</span>
                </div>
              ))}
              {selectedNode.type === 'incident' && (
                <div className="mt-6 border-t border-slate-700 pt-4">
                  <SimilarCasesPanel firId={selectedNode.id} />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
