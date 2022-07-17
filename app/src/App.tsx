import React, { useEffect, useState } from "react";
import LoadingButton from "@mui/lab/LoadingButton";
import "./App.css";
import Flow from "./components/graph_visualiser/graph";
import {
  Alert,
  AppBar,
  Box,
  Button,
  ButtonGroup,
  Grid,
  IconButton,
  Menu,
  MenuItem,
  Snackbar,
  Toolbar,
  Typography,
} from "@mui/material";
import {
  Add,
  AddCircle,
  PlayArrow,
  PlayCircleFilled,
  Save,
} from "@mui/icons-material";
import NodeEditor from "./components/node_editor/editor";
import { ReactFlowProvider } from "react-flow-renderer";
import { APIResponses, GraphType, NodeType } from "./types";
import { addNode, autoLayout } from "./utils/graph_utils";
import { deserialize_graph, serialize_graph } from "./utils/protobuf_utils";
import { HotKeys, configure } from "react-hotkeys";
import moment from "moment";

let ToBase64 = function (u8: any) {
  return btoa(String.fromCharCode.apply(null, u8));
};

configure({
  ignoreTags: ["input", "select"],
  ignoreRepeatedEventsWhenKeyHeldDown: false,
});

function App() {
  const [graph, setGraph] = useState<GraphType>();
  const [snackbarMessage, setSnackbarMessage] = useState<string>("");
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [lastSaved, setLastSaved] = useState<Date>();
  const [busyRunning, setBusyRunning] = useState<boolean>(false);
  const [busySaving, setBusySaving] = useState<boolean>(false);

  // Extracts a graph from the binary response and sets it as the current graph.
  async function handleUpdatedGraph(response: Response) {
    if (response.status == APIResponses.Graph) {
      response.arrayBuffer().then((responseBuffer) => {
        deserialize_graph(
          responseBuffer,
          function (deserialised_graph: GraphType) {
            setGraph((_) => deserialised_graph);
          }
        );
      });
    } else if (response.status == APIResponses.ErrorMessage) {
      // Check if response is a message to display
      setSnackbarMessage(await response.text());
      setSnackbarOpen(true);
    }
  }

  // Saves current graph and updates with the last compiled inputs/outputs.
  async function saveDag(callback?: any) {
    setBusySaving(true);
    if (graph === undefined) {
      setBusySaving(false);
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
        .then(callback)
        .then(() => {
          setBusySaving(false);
          setLastSaved(new Date());
        });
    });
  }

  const runCell = React.useCallback(() => {
    // First save the DAG, to ensure the cell code to be run is up to date.
    setBusyRunning(true);
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
        )
          .then(handleUpdatedGraph)
          .then(() => {
            setBusyRunning(false);
          });
      } else {
        setBusyRunning(false);
      }
    });
  }, [graph]);

  const keyMap = {
    RUN_CELL: "shift+enter",
  };

  const hotkeyHandlers = {
    RUN_CELL: runCell,
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <HotKeys keyMap={keyMap} handlers={hotkeyHandlers} allowChanges={true}>
      <AppBar position="static">
        <Toolbar variant="dense">
          <Typography variant="h6" color="inherit" component="div">
            Graphical Jupyter
          </Typography>
          <Menu
            id="basic-menu"
            // anchorEl={anchorEl}
            open={false}
            // onClose={handleClose}
            MenuListProps={{
              "aria-labelledby": "basic-button",
            }}
            sx={{ width: 320 }}
          >
            <MenuItem dense={true}>Stop the kernel</MenuItem>
            <MenuItem dense={true}>Restart and keep all outputs.</MenuItem>
            <MenuItem dense={true}>Restart and clear all outputs.</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box>
        <Grid container>
          <Grid item xs={6} position="relative">
            {lastSaved ? (
              <Box
                position="absolute"
                style={{ width: "100%", top: -15, zIndex: 999 }}
              >
                <Toolbar style={{ float: "right", fontSize: 12 }}>
                  Last saved:{" "}
                  {moment
                    .utc(lastSaved.toUTCString())
                    .local()
                    .startOf("seconds")
                    .toString()}
                </Toolbar>
              </Box>
            ) : (
              <></>
            )}

            <Box
              position="absolute"
              style={{ width: "100%", top: 20, zIndex: 999 }}
            >
              <Toolbar style={{ float: "right" }}>
                <ButtonGroup
                  variant="contained"
                  aria-label="outlined primary button group"
                  disabled={busySaving || busyRunning}
                >
                  <LoadingButton
                    variant="contained"
                    color="primary"
                    onClick={() => {
                      addNode(setGraph);
                    }}
                    loading={false}
                    startIcon={<AddCircle />}
                  >
                    Add
                  </LoadingButton>
                  <LoadingButton
                    variant="contained"
                    color="primary"
                    onClick={saveDag}
                    loading={busySaving}
                    startIcon={<Save />}
                  >
                    Save
                  </LoadingButton>
                  <LoadingButton
                    variant="contained"
                    color="primary"
                    onClick={runCell}
                    loading={busyRunning}
                    startIcon={<PlayCircleFilled />}
                  >
                    Run
                  </LoadingButton>
                </ButtonGroup>
              </Toolbar>
              <Snackbar
                open={snackbarOpen}
                autoHideDuration={3000}
                anchorOrigin={{ vertical: "top", horizontal: "left" }}
                onClose={handleSnackbarClose}
              >
                <Alert
                  onClose={handleSnackbarClose}
                  severity="error"
                  sx={{ width: "100%" }}
                >
                  {snackbarMessage}
                </Alert>
              </Snackbar>
            </Box>
            <Box
              style={{ position: "relative", width: "100%", height: "100vh" }}
            >
              <ReactFlowProvider>
                <Flow graph={graph} setGraph={setGraph} />
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
