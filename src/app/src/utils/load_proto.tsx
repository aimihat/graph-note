import { load } from "protobufjs"; // respectively "./node_modules/protobufjs"
import { Buffer } from "buffer";
import createGraphLayout from "./flow_layout";
import { decode } from "punycode";

function getEdgesFromConnections(decoded: any) {
  let conns = decoded.connections.map((conn: any) => {
    return { from: conn.fromPort.uid, to: conn.toPort.uid };
  });
  
  var cell_conns: {[port: string]: string} = {};
  decoded.cells.map((cell: any) => {
    cell.inPorts.map((port: any) => {
      cell_conns[port.uid] = cell.uid;
    })
    cell.outPorts.map((port: any) => {
      cell_conns[port.uid] = cell.uid;
    })
  })

  return conns.map((conn: any) => {
    return {id: conn.from, sourceHandle: conn.from, targetHandle: conn.to, source: cell_conns[conn.from], target: cell_conns[conn.to]};
  })
}

function updateFlow(
  root: any,
  serialised_graph: any,
  setNodes: any,
  setEdges: any
) {
  const Graph = root.lookupType("Graph");
  let decoded: any = Graph.decode(new Uint8Array(serialised_graph));
  const new_cells = decoded.cells.map((cell: any) => {
    return { id: cell.uid, type: 'dagNode', data: { label: cell.uid, outputPorts: cell.outPorts, inputPorts: cell.inPorts }, width: 150, height: 50 };
  });

  const nodeLayout = createGraphLayout(new_cells);
  console.log(nodeLayout)
  setNodes(nodeLayout);

  // Load edges
  const edges = getEdgesFromConnections(decoded);
  console.log(edges)
  setEdges(edges);
}

export default function loadGraph(setNodes: any, setEdges: any) {
  // Temporary: load graph from local file

  fetch("http://localhost:8000/read_graph")
    .then((r) => r.arrayBuffer())
    .then((serialised_graph) => {
      load("bundle.json", function (err, root) {
        if (err) throw err;

        if (typeof root === "undefined") throw new Error("root is undefined");

        updateFlow(root, serialised_graph, setNodes, setEdges);
      });
    })
    .catch((error) => console.log(error));
}
