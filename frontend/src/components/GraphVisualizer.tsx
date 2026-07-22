'use client';
import { useEffect, useState, useCallback } from 'react';
import ReactFlow, { 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  Node,
  Edge
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';

export default function GraphVisualizer() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8000/api/v1/graph/suspects')
      .then(res => {
        if (res.data && res.data.nodes) {
          // Layout logic can be complex; doing a simple random distribution for demo
          const formattedNodes: Node[] = res.data.nodes.map((n: any) => ({
            id: n.id,
            position: { x: Math.random() * 600, y: Math.random() * 400 },
            data: { label: n.label },
            style: { 
              background: n.type === 'person' ? '#ef4444' : n.type === 'phone' ? '#3b82f6' : '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '10px'
            }
          }));

          const formattedEdges: Edge[] = res.data.edges.map((e: any, idx: number) => ({
            id: `e${idx}`,
            source: e.source,
            target: e.target,
            label: e.label,
            animated: true,
            style: { stroke: '#94a3b8' }
          }));

          setNodes(formattedNodes);
          setEdges(formattedEdges);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Graph Data Error:", err);
        setLoading(false);
      });
  }, [setNodes, setEdges]);

  if (loading) return <div className="p-4 text-white">Loading Graph Topology...</div>;

  return (
    <div className="h-full w-full rounded-xl overflow-hidden border border-slate-700 bg-slate-900 shadow-2xl">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls className="bg-slate-800 text-white fill-white" />
        <MiniMap nodeStrokeColor="#000" nodeColor="#333" maskColor="rgba(0,0,0,0.5)" />
        <Background color="#334155" gap={16} />
      </ReactFlow>
    </div>
  );
}
