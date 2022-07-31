import React, { useEffect, useState } from "react";
import "./App.css";
import Flow from "./components/graph_visualiser/graph";
import {
  Alert,
  AppBar,
  Box,
  Grid,
  Menu,
  MenuItem,
  Snackbar,
  Toolbar,
  Typography,
} from "@mui/material";
import NodeEditor from "./components/node_editor/editor";
import { ReactFlowProvider } from "react-flow-renderer";
import { BusyStatus } from "./types";
import moment from "moment";
import { AppContext } from "./context/graph_context";
import Controls from "./components/controls/controls";


function App() {
  const [snackbarMessage, setSnackbarMessage] = useState<string | undefined>();
  const [lastSaved, setLastSaved] = useState<Date>();
  const [busyStatus, setBusyStatus] = useState<BusyStatus>(BusyStatus.NotBusy);

  const keyMap = {
    RUN_CELL: "shift+enter",
  };

  const handleSnackbarClose = () => {
    setSnackbarMessage(undefined);
  };

  return (
    <AppContext>
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
              <Controls busyStatus={busyStatus} setBusyStatus={setBusyStatus} setLastSaved={setLastSaved} setSnackbarMessage={setSnackbarMessage}  />
              <Snackbar
                open={snackbarMessage !== undefined}
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
                <Flow />
              </ReactFlowProvider>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <NodeEditor></NodeEditor>
          </Grid>
        </Grid>
      </Box>
    </AppContext>
  );
}

export default App;
