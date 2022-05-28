import React, { useEffect, useState } from "react";
import ReactFlow, {
  Controls,
  MiniMap,
  Node,
  ReactFlowInstance,
} from "react-flow-renderer";
import DAGNode from "./custom_node";

import "./node.scss";
import { GraphType, SetGraphType } from "../../types";
import { deserialize_graph } from "../../utils/protobuf_utils";

const rfStyle = {
  backgroundColor: "#B8CEFF",
};

const nodeTypes = {
  dagNode: DAGNode,
};

interface FlowProps {
  setSelectedNodeId: (arg0: string) => void;
  setGraph: SetGraphType;
  graph?: GraphType;
}

function Flow({ setSelectedNodeId, graph, setGraph }: FlowProps) {
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>();

  const onInit = (rf: ReactFlowInstance) => {
    setReactFlowInstance(rf);

    fetch("http://localhost:8000/read_graph")
      .then((r) => r.arrayBuffer())
      .then((serialised_graph) => {
        deserialize_graph(
          serialised_graph,
          function (deserialised_graph: GraphType) {
            setGraph((_) => deserialised_graph);
          }
        );
      })
      .catch((error) => console.log(error));
  };

  function updateSelectedNode(_: React.MouseEvent, node: Node) {
    setSelectedNodeId(node.id);
  }

  useEffect(() => {
    if (reactFlowInstance) {
      reactFlowInstance.fitView();
    }
  }, [graph?.nodes.length]);

  return (
    <ReactFlow
      nodes={graph?.nodes}
      edges={graph?.edges}
      nodeTypes={nodeTypes}
      style={rfStyle}
      onInit={onInit}
      onNodeClick={updateSelectedNode}
      fitView
    >
      <MiniMap />
      <Controls />
    </ReactFlow>
  );
}

export default Flow;
