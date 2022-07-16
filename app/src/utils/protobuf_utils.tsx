import { load, Message } from "protobufjs"; // respectively "./node_modules/protobufjs"
import { EdgeType, GraphType, NodeType } from "../types";
import { autoLayout } from "./graph_utils";

export type GraphMessageType = any;

function parse_message(deserialized_message: GraphMessageType): GraphType {
  // Parse graph-level attributes
  const selectedCell = deserialized_message.selectedCell;

  // Parse edges (can be made more efficient by caching port -> nodeid map)
  console.log(deserialized_message);
  const edges = deserialized_message.connections.map((conn: any) => {
    return {
      id: `${conn.sourceUid} + ${conn.TargetUid}`,
      sourceHandle: conn.sourceUid,
      targetHandle: conn.targetUid,
      source: deserialized_message.cells.find((node: any) => {
        return node.outPorts.map((p: any) => p.uid)?.includes(conn.sourceUid);
      })?.uid, // todo: remove this when pruning connections
      target: deserialized_message.cells.find((node: any) =>
        node.inPorts.map((p: any) => p.uid)?.includes(conn.targetUid)
      )?.uid, // todo: remove this when pruning connections
    };
  });

  // Parse nodes
  const nodes = autoLayout(
    deserialized_message.cells.map((cell: any) => {
      return {
        id: cell.uid,
        type: "dagNode",
        data: {
          output: cell.output,
          outputPorts: cell.outPorts,
          inputPorts: cell.inPorts,
          code: cell.code,
          dependencyStatus: cell.dependencyStatus
        },
        width: 150,
        height: 50,
        selected: cell.uid === selectedCell,
      };
    }),
    edges
  );
  const graph = {
    nodes: nodes,
    edges: edges,
    selectedCell: selectedCell,
  };

  return graph;
}

export function deserialize_graph(
  serialized_graph: ArrayBuffer,
  callback: (arg0: GraphType) => void
) {
  load("bundle.json", function (err, root) {
    if (err) throw err;

    if (typeof root === "undefined") throw new Error("root is undefined");

    const Graph = root.lookupType("Graph");
    let deserialised_graph: GraphType = parse_message(
      Graph.decode(new Uint8Array(serialized_graph))
    );

    callback(deserialised_graph);
  });
}

export function serialize_graph(
  graph: GraphType,
  callback: (arg0: Uint8Array) => void
) {
  load("bundle.json", function (err, root) {
    if (err) throw err;

    if (typeof root === "undefined") throw new Error("root is undefined");

    const Graph = root.lookupType("Graph");

    // Create cells
    const protoNodes = graph.nodes.map((node) =>
      root.lookupType("Cell").create({
        uid: node.id,
        code: node.data.code,
        inPorts:
          node.data.inputPorts?.map((p) => root.lookupType("Port").create(p)) ??
          [],
        outPorts:
          node.data.outputPorts?.map((p) =>
            root.lookupType("Port").create(p)
          ) ?? [],
        output: node.data.output,
        dependencyStatus: node.data.dependencyStatus
      })
    );

    const allPorts = graph.nodes.flatMap((node) =>
      (node.data.inputPorts ?? []).concat(node.data.outputPorts ?? [])
    );

    // Create edges
    const protoConnections = graph.edges.map((edge: EdgeType) =>
      root.lookupType("Connection").create({
        sourceUid: edge.sourceHandle,
        targetUid: edge.targetHandle,
      })
    );

    // Create graph
    const graphMessage = Graph.create({
      cells: protoNodes,
      connections: protoConnections,
      selectedCell: graph.selectedCell,
    });

    // TODO: handle root node.
    var verifErr = Graph.verify(graphMessage);
    if (verifErr) throw Error(verifErr);

    callback(Graph.encode(graphMessage).finish());
  });
}
