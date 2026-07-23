'use client';
import { useEffect, useState } from 'react';
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
import { ZoomIn, ZoomOut, Maximize } from 'lucide-react';

const CustomZoomControls = () => {
  const { zoomIn, zoomOut, fitView } = useReactFlow();
  
  return (
    <Panel position="bottom-left" className="flex flex-col gap-2 bg-slate-800/90 p-2 rounded-lg border border-slate-700 shadow-xl backdrop-blur-sm mb-4 ml-2">
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

    // Shift Dagre's center-based positioning to React Flow's top-left based positioning
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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    axios.get(`${API_URL}/api/v1/graph/suspects`)
      .then(res => {
        if (res.data && res.data.nodes) {
          
          const rawNodes: Node[] = res.data.nodes.map((n: any) => ({
            id: n.id,
            position: { x: 0, y: 0 }, // Will be overridden by dagre
            data: { label: n.label },
            style: { 
              background: n.type === 'accused' ? '#ef4444' : n.type === 'incident' ? '#3b82f6' : n.type === 'complainant' ? '#10b981' : n.type === 'victim' ? '#f59e0b' : '#8b5cf6',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '8px',
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

          // Apply Dagre layout (Top to Bottom)
          const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
            rawNodes,
            rawEdges,
            'TB'
          );

          setNodes(layoutedNodes);
          setEdges(layoutedEdges);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Graph Data Error:", err);
        setLoading(false);
      });
  }, [setNodes, setEdges]);

  if (loading) return <div className="p-4 text-white flex items-center justify-center h-full">Calculating Graph Topology...</div>;

  return (
    <div className="h-full w-full rounded-xl overflow-hidden border border-slate-700 bg-slate-900 shadow-2xl relative">
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          attributionPosition="bottom-right"
        >
          <Background color="#475569" gap={20} size={1.5} />
          <CustomZoomControls />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}
