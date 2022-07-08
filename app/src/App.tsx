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
import { HotKeys } from "react-hotkeys";

let ToBase64 = function (u8: any) {
  return btoa(String.fromCharCode.apply(null, u8));
};

function App() {
  const [graph, setGraph] = useState<GraphType>();

  // Extracts a graph from the binary response and sets it as the current graph.
  function handleUpdatedGraph(response: Response) {
    response.arrayBuffer().then((responseBuffer) => {
      deserialize_graph(
        responseBuffer,
        function (deserialised_graph: GraphType) {
          console.log(deserialised_graph)
          setGraph((_) => deserialised_graph);
        }
      );
    });
  }

  // Saves current graph and updates with the last compiled inputs/outputs.
  async function saveDag(callback?: any) {
    if (graph === undefined) {
      return;
    }
    serialize_graph(graph, function (u8: Uint8Array) {
      var b64 = ToBase64(u8);
      fetch("http://localhost:8000/save_graph", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ b64_graph: b64 }),
      })
        .then(handleUpdatedGraph)
        .then(callback);
    });
  }

  function runCell() {
    // First save the DAG, to ensure the cell code to be run is up to date.
    saveDag(() => {
      // run_cell with the selected node's id
      if (graph?.selectedCell !== undefined) {
        fetch(
          `http://localhost:8000/run_cell?cell_uid=${encodeURIComponent(
            graph.selectedCell
          )}`,
          {
            method: "GET",
          }
        ).then(handleUpdatedGraph);
      }
    });
  }

  const keyMap = {
    RUN_CELL: "shift+enter",
  }

  const hotkeyHandlers = {
    RUN_CELL: runCell
  }

  return (
    <HotKeys keyMap={keyMap} handlers={hotkeyHandlers}>
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
              <Button
                sx={{ mx: 1 }}
                variant="outlined"
                color="secondary"
                aria-label="add"
                title=""
                onClick={runCell}
              >
                Run cell
                <Save sx={{ mx: 1 }} />
              </Button>
            </Toolbar>
            <Box style={{ position: "relative", width: "100%", height: "100vh" }}>
              <ReactFlowProvider>
                <Flow
                  graph={graph}
                  setGraph={setGraph}
                />
              </ReactFlowProvider>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <NodeEditor
              node={graph?.nodes.find(
                (node: NodeType) => node.id == graph.selectedCell
              )}
              setGraph={setGraph}
            ></NodeEditor>
          </Grid>
        </Grid>
      </Box>
    </HotKeys>
  );
}

export default App;
