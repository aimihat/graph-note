import { XYPosition } from "react-flow-renderer";

export type SetGraphType = (
  _?: (_?: GraphType) => GraphType | undefined
) => void;

export type PortType = {
  uid: string;
  name: string;
};

export type NodeDataType = {
  label?: string;
  output?: string;
  code?: string;
  inputPorts?: PortType[];
  outputPorts?: PortType[];
};

export type NodeType = {
  id: string;
  type: string;
  data: NodeDataType;
  width: number;
  height: number;
  position: XYPosition;
};

export type EdgeType = {
  id: string;
  sourceHandle: string;
  targetHandle: string;
  source: string;
  target: string;
};

/* Client uses a graph data-structure that's easy to consume with ReactFlow */
export type GraphType = {
  nodes: NodeType[];
  edges: EdgeType[];
  root?: NodeType; // TODO: not optional.
};
