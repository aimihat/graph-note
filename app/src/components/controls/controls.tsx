import React, { useEffect, useState } from "react";
import { APIResponses, BusyStatus, GraphType, NodeType } from "../../types";
import { deserialize_graph, serialize_graph } from "../../utils/protobuf_utils";
import LoadingButton from "@mui/lab/LoadingButton";
import { ButtonGroup, Toolbar } from "@mui/material";
import {
  Add,
  ContentCutSharp,
  PlayArrow,
  RestartAlt,
  RestartAltSharp,
  Save,
  SaveSharp,
  Stop,
  StopCircle,
} from "@mui/icons-material";
import { addNode } from "../../utils/graph_utils";
import { useGraph, useSetGraph } from "../../context/graph_context";

interface ControlsProps {
  busyStatus: BusyStatus;
  setBusyStatus: React.Dispatch<React.SetStateAction<BusyStatus>>;
  setLastSaved: React.Dispatch<React.SetStateAction<Date | undefined>>;
  setSnackbarMessage: React.Dispatch<React.SetStateAction<string | undefined>>;
}

let ToBase64 = function (u8: any) {
  return btoa(String.fromCharCode.apply(null, u8));
};

function Controls({
  setLastSaved,
  setSnackbarMessage,
  busyStatus,
  setBusyStatus,
}: ControlsProps) {
  const graph = useGraph();
  const setGraph = useSetGraph();
  // TODO: do not make requests for run_cell, etc. when busyStatus != notbusy
  async function restartKernel() {
    setBusyStatus(BusyStatus.BusySaving);

    fetch("http://localhost:8000/restart_kernel")
      .then((r) => r.arrayBuffer())
      .then((serialised_graph) => {
        deserialize_graph(
          serialised_graph,
          function (deserialised_graph: GraphType) {
            setGraph((_) => deserialised_graph);
            setBusyStatus(BusyStatus.NotBusy);
          }
        );
      })
      .catch((error) => console.log(error));
  }

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
    }
  }

  // Saves current graph and updates with the last compiled inputs/outputs.
  async function saveDag(callback?: any) {
    setBusyStatus(BusyStatus.BusySaving);
    if (graph === undefined) {
      setBusyStatus(BusyStatus.NotBusy);
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
          setBusyStatus(BusyStatus.NotBusy);
          setLastSaved(new Date());
        });
    });
  }

  const runCell = React.useCallback(() => {
    // First save the DAG, to ensure the cell code to be run is up to date.
    setBusyStatus(BusyStatus.BusyRunning);
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
            setBusyStatus(BusyStatus.NotBusy);
          });
      } else {
        setBusyStatus(BusyStatus.NotBusy);
      }
    });
  }, [graph]);

  return (
    <Toolbar style={{ float: "right" }}>
      <ButtonGroup
        sx={{ m: 1 }}
        size="small"
        variant="contained"
        aria-label="outlined primary button group"
      >
        <LoadingButton variant="contained" color="primary" onClick={saveDag}>
          <SaveSharp />
        </LoadingButton>
      </ButtonGroup>
      <ButtonGroup
        sx={{ m: 1 }}
        size="small"
        variant="contained"
        aria-label="outlined primary button group"
      >
        <LoadingButton
          variant="contained"
          color="primary"
          onClick={() => {
            addNode(setGraph);
          }}
          loading={false}
        >
          <Add />
        </LoadingButton>
        <LoadingButton
          variant="contained"
          color="primary"
          onClick={() => {}}
          loading={false}
        >
          <ContentCutSharp />
        </LoadingButton>
      </ButtonGroup>
      <ButtonGroup
        sx={{ m: 1 }}
        size="small"
        variant="contained"
        aria-label="outlined primary button group"
      >
        <LoadingButton
          variant="contained"
          color="primary"
          onClick={runCell}
          style={{ textTransform: "none" }}
        >
          <PlayArrow sx={{ mr: 0.5 }} />
          Run
        </LoadingButton>
        <LoadingButton variant="contained" color="primary">
          <Stop />
        </LoadingButton>
        <LoadingButton
          variant="contained"
          color="primary"
          onClick={restartKernel}
        >
          <RestartAlt />
        </LoadingButton>
      </ButtonGroup>
    </Toolbar>
  );
}

export default Controls;
