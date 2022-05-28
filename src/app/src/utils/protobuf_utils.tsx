import { load, Message } from "protobufjs"; // respectively "./node_modules/protobufjs"
import { EdgeType, GraphType, NodeType } from "../types";
import { autoLayout } from "./graph_utils";

export type GraphMessageType = any;

function parse_message(deserialized_message: GraphMessageType): GraphType {
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
        },
        width: 150,
        height: 50,
      };
    })
  );

  // Parse edges (can be made more efficient by caching port -> nodeid map)
  const edges = deserialized_message.connections.map((conn: any) => {
    return {
      id: conn.fromPort.uid, // arbitrary but must be unique
      sourceHandle: conn.fromPort.uid,
      targetHandle: conn.toPort.uid,
      source: deserialized_message.cells.find((node: any) => {
        return node.outPorts
          .map((p: any) => p.uid)
          ?.includes(conn.fromPort.uid);
      }).uid,
      target: deserialized_message.cells.find((node: any) =>
        node.inPorts.map((p: any) => p.uid)?.includes(conn.toPort.uid)
      ).uid,
    };
  });

  const graph = {
    nodes: nodes,
    edges: edges,
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
        in_ports: node.data.outputPorts,
        out_ports: node.data.inputPorts,
        output: node.data.output,
      })
    );
    // Create edges
    const protoConnections = graph.edges.map((edge) =>
      root.lookupType("Connection").create({
        from_port: edge.sourceHandle,
        to_port: edge.targetHandle,
      })
    );

    // Create graph
    const graphMessage = Graph.create({
      cells: protoNodes,
      connections: protoConnections,
    });

    // TODO: handle root node.
    var verifErr = Graph.verify(graphMessage);
    if (verifErr) throw Error(verifErr);

    callback(Graph.encode(graphMessage).finish());
  });
}
