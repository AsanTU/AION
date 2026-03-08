import React, { useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";

export default function GraphVisualizer({ data, onNodeClick }) {
  const fgRef = useRef();

  return (
    <ForceGraph2D
      ref={fgRef}
      graphData={data}
      nodeLabel={node => `
        <b>${node.label}</b><br/>
        Confidence: ${node.confidence}<br/>
        ${node.reasoning}
      `}
      nodeAutoColorBy="disagreement"
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.label;
        const fontSize = 12/globalScale;
        ctx.font = `${fontSize}px Sans-Serif`;
        ctx.fillStyle = node.disagreement ? "red" : "green";
        ctx.beginPath();
        ctx.arc(node.x, node.y, 8 + node.confidence * 10, 0, 2 * Math.PI, false);
        ctx.fill();
        ctx.fillStyle = "black";
        ctx.fillText(label, node.x + 12, node.y + 4);
      }}
      linkColor={link => link.type === "disagrees" ? "red" : "gray"}
      onNodeClick={onNodeClick}
    />
  );
}