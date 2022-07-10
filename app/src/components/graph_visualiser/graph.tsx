import React, { useCallback, useEffect, useState } from "react";
import ReactFlow, {
  Controls,
  MiniMap,
  Node,
  ReactFlowInstance,
  applyEdgeChanges,
  applyNodeChanges,
  NodeChange,
  EdgeChange,
  Edge,
  useEdgesState,
  addEdge,
  Connection,
} from "react-flow-renderer";
import DAGNode from "./custom_node";

import "./node.scss";
import { EdgeType, GraphType, NodeType, SetGraphType } from "../../types";
import { deserialize_graph } from "../../utils/protobuf_utils";

const rfStyle = {
  backgroundColor: "#B8CEFF",
};

const nodeTypes = {
  dagNode: DAGNode,
};

interface FlowProps {
  setGraph: SetGraphType;
  graph?: GraphType;
}

function Flow({ graph, setGraph }: FlowProps) {
  const onConnect = (params: Connection) => {
    setGraph((prevGraph?: GraphType) => {
      if (prevGraph === undefined) {
        console.log("Cannot update node on undefined graph.");
        return undefined;
      }

      const updatedGraph = { ...prevGraph };
      const newEdge = {...params, id: `${params.sourceHandle} + ${params.targetHandle}`} as EdgeType;
      updatedGraph.edges.push(newEdge)

      return updatedGraph;
    }); 
  }

  const onEdgesDelete = (edges: Edge<any>[]) => {
    setGraph((prevGraph?: GraphType) => {
      if (prevGraph === undefined) {
        console.log("Cannot update node on undefined graph.");
        return undefined;
      }

      const deletedEdgeIds = edges.map(x=>x.id)

      const updatedGraph = { ...prevGraph }; // TODO: correct way to copy?
      console.log('Deleting ', deletedEdgeIds);
      updatedGraph.edges = prevGraph.edges.filter(edge => !deletedEdgeIds.includes(edge.id))

      return updatedGraph;
    }); 
  }
  // Update edges when graph changes
  // useEffect(() => {
  //   if (graph?.edges !== undefined) {
  //     setEdges(graph?.edges);
  //   }
  // }, [graph]);

  // // Update graph when edges change (i.e. when edited)
  // useEffect(() => {
  //   setGraph((prevGraph?: GraphType) => {
  //     if (prevGraph === undefined) {
  //       console.log("Cannot update node on undefined graph.");
  //       return undefined;
  //     }

  //     const updatedGraph = { ...prevGraph }; // TODO: correct way to copy?
  //     updatedGraph.edges = edges as EdgeType[];

  //     return updatedGraph;
  //   });
  // }, [edges]);

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
    console.log("Updating selected node in graph to " + node.id, graph);
    setGraph((prevGraph?: GraphType) => {
      if (prevGraph === undefined) return undefined;
      const updatedGraph = { ...prevGraph };
      updatedGraph.selectedCell = node.id;
      return updatedGraph;
    });
    console.log("Updating selected node in graph to " + node.id, graph);
  }

  useEffect(() => {
    if (reactFlowInstance) {
      reactFlowInstance.fitView();
    }
  }, [graph?.nodes.length]);

  useEffect(() => console.log("Graph was updated", graph), [graph])
  return (
    <ReactFlow
      nodes={graph?.nodes}
      edges={graph?.edges}
      onConnect={onConnect}
      onEdgesDelete={onEdgesDelete}
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
