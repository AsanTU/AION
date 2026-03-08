import React, { useState, useEffect } from "react";
import GraphVisualizer from "./GraphVisualizer";

const sampleData = {
  nodes: [
    { id: "1", label: "Agent 1", reasoning: "Reason 1", confidence: 0.8, disagreement: false },
    { id: "2", label: "Agent 2", reasoning: "Reason 2", confidence: 0.6, disagreement: true }
  ],
  links: [
    { source: "1", target: "2", type: "disagrees" }
  ]
};

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    // Fetch your graph data from backend API
    fetch("http://localhost:8000/api/graph") // Adjust URL as needed
      .then(res => res.json())
      .then(setGraphData);
  }, []);

  return (
    <div>
      <h1>Explainable Multi-Agent AI System</h1>
      <GraphVisualizer
        data={sampleData}
        onNodeClick={setSelectedNode}
      />
      {selectedNode && (
        <div style={{ position: "absolute", right: 20, top: 20, background: "#fff", padding: 20, border: "1px solid #ccc" }}>
          <h2>Node Details</h2>
          <p><b>Label:</b> {selectedNode.label}</p>
          <p><b>Reasoning:</b> {selectedNode.reasoning}</p>
          <p><b>Confidence:</b> {selectedNode.confidence}</p>
        </div>
      )}
    </div>
  );
}

export default App;