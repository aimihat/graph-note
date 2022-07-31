import React, { useCallback, useEffect, useState } from "react";
import ReactFlow, {
  Controls,
  MiniMap,
  Node,
  ReactFlowInstance,
  Edge,
  Connection,
} from "react-flow-renderer";
import DAGNode from "./custom_node";

import "./node.scss";
import { EdgeType, GraphType, NodeType, SetGraphType } from "../../types";
import { deserialize_graph } from "../../utils/protobuf_utils";
import { autoLayout } from "../../utils/graph_utils";
import { useGraph, useSetGraph } from "../../context/graph_context";

const rfStyle = {
  backgroundColor: "#eee",
};

const nodeTypes = {
  dagNode: DAGNode,
};

interface FlowProps {
  setGraph: SetGraphType;
  graph?: GraphType;
}

function Flow() {
  const graph = useGraph()
  const setGraph = useSetGraph()

  const onConnect = (params: Connection) => {
    setGraph((prevGraph?: GraphType) => {
      if (prevGraph === undefined) {
        console.log("Cannot update node on undefined graph.");
        return undefined;
      }
      const updatedGraph = { ...prevGraph };

      // Delete all other edges connecting to target port:
      updatedGraph.edges = updatedGraph.edges.filter(
        (e) => e.targetHandle != params.targetHandle
      );

      const newEdge = {
        ...params,
        id: `${params.sourceHandle} + ${params.targetHandle}`,
      } as EdgeType;

      updatedGraph.edges.push(newEdge);
      updatedGraph.nodes = autoLayout(prevGraph.nodes, updatedGraph.edges);

      return updatedGraph;
    });
  };

  const onEdgesDelete = (edges: Edge<any>[]) => {
    setGraph((prevGraph?: GraphType) => {
      if (prevGraph === undefined) {
        console.log("Cannot update node on undefined graph.");
        return undefined;
      }

      const deletedEdgeIds = edges.map((x) => x.id);

      const updatedGraph = { ...prevGraph }; // TODO: correct way to copy?
      console.log("Deleting ", deletedEdgeIds);
      updatedGraph.edges = prevGraph.edges.filter(
        (edge) => !deletedEdgeIds.includes(edge.id)
      );
      updatedGraph.nodes = autoLayout(prevGraph.nodes, updatedGraph.edges);

      return updatedGraph;
    });
  };

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
    setGraph((prevGraph?: GraphType) => {
      if (prevGraph === undefined) return undefined;
      const updatedGraph = { ...prevGraph };
      updatedGraph.selectedCell = node.id;
      return updatedGraph;
    });
  }

  function deselectNode(_: React.MouseEvent) {
    setGraph((prevGraph?: GraphType) => {
      if (prevGraph === undefined) return undefined;
      const updatedGraph = { ...prevGraph };
      updatedGraph.selectedCell = undefined;
      return updatedGraph;
    });
  }

  useEffect(() => {
    if (reactFlowInstance) {
      reactFlowInstance.fitView();
    }
  }, [graph?.nodes.length]);

  useEffect(() => console.log("Graph was updated", graph), [graph]);

  return (
    <ReactFlow
      nodes={graph?.nodes.map((n) => {
        return { ...n, selected: n.id == graph?.selectedCell };
      })}
      edges={graph?.edges}
      onConnect={onConnect}
      onEdgesDelete={onEdgesDelete}
      onPaneClick={deselectNode}
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
