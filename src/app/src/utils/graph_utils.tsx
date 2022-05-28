import { GraphType, NodeType, SetGraphType } from "../types";
import dagre from "dagre";
var _ = require('lodash');

export function updateNode(
  nodeId: string,
  partialNode: Partial<NodeType>,
  setGraph: SetGraphType
) {
  // Overrides node with given `nodeId` with any properties defined in `partialNode`.
  setGraph((prevGraph?: GraphType) => {
    if (prevGraph === undefined) {
      console.log("Cannot update node on undefined graph.");
      return undefined;
    }

    const prevNodes = prevGraph.nodes;
    const updatedNodes = prevNodes.map((node: NodeType) => {
      if (node.id == nodeId) {
        return _.merge(node, partialNode)
      }

      return node;
    });

    // If node id was updated, update edges to match
    let updatedEdges = prevGraph.edges;
    const newNodeId = partialNode.id;
    if (newNodeId !== undefined) {
      updatedEdges = prevGraph.edges.map(edge => {
        edge.target = edge.target.replace(nodeId, newNodeId)
        edge.source = edge.source.replace(nodeId, newNodeId)
        return edge
      })
    }

    const updatedGraph = { ...prevGraph }; // TODO: correct way to copy?
    updatedGraph.nodes = updatedNodes;
    updatedGraph.edges = updatedEdges;

    return updatedGraph;
  });
  
}

export function addNode(setGraph: SetGraphType) {
  const newNodeIdPrefix = "new-node-";
  const newNodeId = newNodeIdPrefix + Math.random().toString(36).slice(2, 7);
  const newEmptyNode: NodeType = {
    id: newNodeId,
    type: "dagNode",
    data: { },
    width: 150,
    height: 50,
    position: { x: 0, y: 0 },
  };

  setGraph((prevGraph?: GraphType) => {
    if (prevGraph === undefined) {
      console.log("Cannot update node on undefined graph.");
      return undefined;
    }
    const prevNodes = prevGraph.nodes;
    const updatedNodes = autoLayout([...prevNodes, newEmptyNode]);

    const updatedGraph = { ...prevGraph }; // TODO: correct way to copy?
    updatedGraph.nodes = updatedNodes;

    return updatedGraph;
  });
}

export const autoLayout = (flowNodeStates: NodeType[]): NodeType[] => {
  // Takes an array of Nodes, and positions them according to dependencies.

  const g = new dagre.graphlib.Graph({ directed: true });
  g.setGraph({ rankdir: "network-simplex" });

  // Default to assigning a new object as a label for each new edge.
  g.setDefaultEdgeLabel(() => ({}));

  flowNodeStates.forEach((node) => {
    g.setNode(node.id, {
      width: node.width,
      height: node.height,
      inputPorts: node.data.inputPorts,
      outputPorts: node.data.outputPorts,
      output: node.data.output,
      code: node.data.code,
      type: node.type,
    });

    // TODO: set edges based on your data structure of the graph.
    // node.data.outputPorts &&
    //   node.data.outBoundEdges.forEach((edge: any) => {
    //     g.setEdge(node.id, edge.targetNodeId);
    //   });
  });

  dagre.layout(g);

  return flowNodeStates.map((nodeState) => {
    const node = g.node(nodeState.id);
    return {
      ...nodeState,
      position: {
        // The position from dagre layout is the center of the node.
        // Calculating the position of the top left corner for rendering.
        x: node.x - node.width / 2,
        y: node.y - node.height / 2,
      },
    };
  });
};
