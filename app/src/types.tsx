import { XYPosition } from "react-flow-renderer";

export type SetGraphType = (
  _?: (_?: GraphType) => GraphType | undefined
) => void;

export type PortType = {
  uid: string;
  name: string;
};

export type NodeDataType = {
  output?: string;
  code?: string;
  inputPorts?: PortType[];
  outputPorts?: PortType[];
  dependencyStatus?: DependencyStatus;
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
  selectedCell?: string;
};

export enum APIResponses {
  Graph = 200,
  ErrorMessage = 206
}

export enum DependencyStatus {
  NotExecuted = 0,
  InputPortOutdated = 1,
  UpToDate = 2,
  // @future: consider a state for code being updated?
}

export enum BusyStatus {
  NotBusy = 0,
  BusyRunning = 1,
  BusySaving = 2,
}
