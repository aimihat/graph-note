import React, { useState } from "react";
import "./App.css";
import Flow from "./components/graph_visualiser/graph";
import { Box, Button, Grid, Toolbar } from "@mui/material";
import { Add, Save } from "@mui/icons-material";
import NodeEditor from "./components/node_editor/editor";
import { ReactFlowProvider } from "react-flow-renderer";
import { GraphType, NodeType } from "./types";
import { addNode } from "./utils/graph_utils";
import { deserialize_graph, serialize_graph } from "./utils/protobuf_utils";

function App() {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [graph, setGraph] = useState<GraphType>();

  // Saves current graph and updates with the last compiled inputs/outputs.
  function saveDag() {
    if (graph === undefined) {
      return;
    }
    serialize_graph(graph, function (buffer: Uint8Array) {
      fetch("http://localhost:8000/save_graph", {
        method: "POST",
        body: buffer,
      }).then((response) => {
        response.arrayBuffer().then(responseBuffer => {
          deserialize_graph(
            responseBuffer,
            function (deserialised_graph: GraphType) {
              setGraph((_) => deserialised_graph);
            }
          );
        })
      });
    });
  }

  return (
    <Box>
      <Grid container>
        <Grid item xs={6} position="relative">
          <Toolbar
            style={{ position: "absolute", zIndex: 999, top: 20, right: 20 }}
          >
            <Button
              sx={{ mx: 1 }}
              variant="outlined"
              color="primary"
              aria-label="add"
              title=""
              onClick={() => {
                addNode(setGraph);
              }}
            >
              New node
              <Add sx={{ mx: 1 }} />
            </Button>
            <Button
              sx={{ mx: 1 }}
              variant="outlined"
              color="secondary"
              aria-label="add"
              title=""
              onClick={saveDag}
            >
              Save DAG
              <Save sx={{ mx: 1 }} />
            </Button>
          </Toolbar>
          <Box style={{ position: "relative", width: "100%", height: "100vh" }}>
            <ReactFlowProvider>
              <Flow
                setSelectedNodeId={setSelectedNodeId}
                graph={graph}
                setGraph={setGraph}
              />
            </ReactFlowProvider>
          </Box>
        </Grid>
        <Grid item xs={6}>
          <NodeEditor
            node={graph?.nodes.find(
              (node: NodeType) => node.id == selectedNodeId
            )}
            setGraph={setGraph}
            setSelectedNodeId={setSelectedNodeId}
          ></NodeEditor>
        </Grid>
      </Grid>
    </Box>
  );
}

export default App;
