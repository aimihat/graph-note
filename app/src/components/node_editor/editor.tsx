import Ansi from "ansi-to-react";
import Editor from "@monaco-editor/react";
import {
  HighlightAltSharp,
} from "@mui/icons-material";
import {
  Box,
  Container,
  Divider,
  TextField,
  Typography,
} from "@mui/material";
import React, { useEffect, useRef, useState } from "react";
import { GraphType, NodeType, SetGraphType } from "../../types";
import { updateNode } from "../../utils/graph_utils";
import { useGraph, useSetGraph } from "../../context/graph_context";
interface NodeEditorProps {
  node?: NodeType;
  setGraph: SetGraphType;
}

function NodeEditor() {
  const graph = useGraph();
  const setGraph = useSetGraph();
  const node = graph?.nodes.find(
    (node: NodeType) => node.id == graph.selectedCell
  );
  const [nodeCode, setNodeCode] = useState(node?.data?.code);

  useEffect(() => {
    // TODO: why is this necessary?
    setNodeCode(node?.data?.code);
  }, [node?.data?.code]);

  // No cell selected.
  if (node === undefined) {
    return (
      <Typography variant="overline" color="grey">
        <Box
          style={{
            display: "flex",
            alignItems: "center",
            flexWrap: "wrap",
            flexDirection: "column",
            fontSize: "20px",
            justifyContent: "center",
            minHeight: "90vh",
          }}
        >
          <HighlightAltSharp fontSize="large" sx={{ mx: 2 }} />
          Select a cell to edit it
        </Box>
      </Typography>
    );
  }

  // Display cell output.
  let cell_output = (
    <Container sx={{ mt: 2 }}>
      <div style={{ fontSize: 12 }}>
        <Ansi>{node.data.output ?? ""}</Ansi>
      </div>
    </Container>
  );

  return (
    <>
      <Container>
        <Box paddingY={2}>
          <TextField
            id="node-id"
            label="Node name"
            variant="outlined"
            size="small"
            value={node.id}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
              updateNode(node?.id, { id: event.target.value }, setGraph);
              setGraph((prevGraph?: GraphType) => {
                if (prevGraph === undefined) return undefined;
                const updatedGraph = { ...prevGraph };
                updatedGraph.selectedCell = event.target.value;
                return updatedGraph;
              });
            }}
          />
        </Box>
        <Editor
          height="55vh"
          defaultLanguage="python"
          value={nodeCode}
          onChange={(code?: string) => {
            updateNode(node?.id, { data: { code: code } }, setGraph);
          }}
        />
      </Container>
      <Divider></Divider>
      <pre
        style={{
          height: "38vh",
          overflow: "scroll",
          overflowY: "auto",
          margin: 0,
        }}
      >
        {cell_output}
      </pre>
    </>
  );
}

export default NodeEditor;
