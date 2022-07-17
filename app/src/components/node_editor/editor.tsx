import Ansi from "ansi-to-react";
import Editor from "@monaco-editor/react";
import { AccessTime, PrecisionManufacturing } from "@mui/icons-material";
import {
  Alert,
  AlertTitle,
  Box,
  Card,
  CardContent,
  Container,
  Divider,
  Paper,
  TextField,
  Typography,
} from "@mui/material";
import React, { useEffect, useRef, useState } from "react";
import { GraphType, NodeType, SetGraphType } from "../../types";
import { updateNode } from "../../utils/graph_utils";

interface NodeEditorProps {
  node?: NodeType;
  setGraph: SetGraphType;
}

function NodeEditor({ node, setGraph }: NodeEditorProps) {
  const [nodeCode, setNodeCode] = useState(node?.data?.code);

  useEffect(() => {
    // TODO: why is this necessary?
    setNodeCode(node?.data?.code)
  }, [node?.data?.code])

  // No cell selected.
  if (node === undefined) {
    return (
      <Box sx={{ my: 2, mx: 2 }}>
        <h3>Select or create a node</h3>
      </Box>
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
