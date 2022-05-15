import React from "react";
import logo from "./logo.svg";
import "./App.css";
import Flow from "./components/graph";
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Container,
  Fab,
  Grid,
  IconButton,
  TextField,
  Toolbar,
  Typography,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { Add, Save } from "@mui/icons-material";
import Editor from "@monaco-editor/react";

function App() {
  return (
    <Box>
      <Grid container>
        <Grid item xs={8} position="relative">
          <Toolbar
            style={{ position: "absolute", zIndex: 999, top: 20, right: 20 }}
          >
            <Fab variant="extended" color="primary" aria-label="add">
              <Add />
            </Fab>
            <Fab color="secondary" aria-label="add">
              <Save />
            </Fab>
          </Toolbar>
          <Box style={{ position: "relative", width: "100%", height: "100vh" }}>
            <Flow />
          </Box>
        </Grid>
        <Grid item xs={4}>
          <Container>
            <h3>Cell_visualize</h3>
            <Editor
              height="60vh"
              defaultLanguage="python"
              defaultValue="# some comment"
            />
            <Alert severity="error">
              <AlertTitle>Errors</AlertTitle>
              This is an error alert — <strong>check it out!</strong>
            </Alert>
            <Alert severity="info">
              <AlertTitle>Output</AlertTitle>
              This is an info alert — <strong>check it out!</strong>
            </Alert>
          </Container>
        </Grid>
      </Grid>
    </Box>
  );
}

export default App;
