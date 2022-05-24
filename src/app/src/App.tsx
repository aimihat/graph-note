import React, { useState } from "react";
import "./App.css";
import Flow from "./components/graph_visualiser/graph";
import { Box, Button, Grid, Toolbar } from "@mui/material";
import { Add, Save } from "@mui/icons-material";
import NodeEditor from "./components/node_editor/editor";
import { ReactFlowProvider } from "react-flow-renderer";
import { EdgeType, GraphType, NodeType } from "./types";
import { addNode, updateNode } from "./utils/graph_utils";

const TEMP_NO_OP = (_: any) => {};

function App() {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [graph, setGraph] = useState<GraphType>();

  function saveDag() {
    // convert back to proto
    // call saveDag endpoint
    // todo: update dag using newly compiled ports
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
