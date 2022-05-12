import dagre, { GraphLabel } from 'dagre';
import DAGNode from './custom_node';

const createGraphLayout = (flowNodeStates: any[]): any[] => {
  const g = new dagre.graphlib.Graph({ directed: true });
  g.setGraph({ rankdir: 'network-simplex' });

  // Default to assigning a new object as a label for each new edge.
  g.setDefaultEdgeLabel(() => ({}));

  flowNodeStates.forEach((node) => {
    g.setNode(node.id, {
      label: node.id,
      width: node.width,
      height: node.height,
      inputPorts: node.inputPorts,
      outputPorts: node.outputPorts,
      type: node.type
    });
    // My node data contains out bound edges. You can set edge based on your data structure of the graph.
    node.data.outBoundEdges &&
      node.data.outBoundEdges.forEach((edge: any) => {
        g.setEdge(node.id, edge.targetNodeId);
      });
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

export default createGraphLayout;