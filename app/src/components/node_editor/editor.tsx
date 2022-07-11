import Ansi from "ansi-to-react";
import Editor from "@monaco-editor/react";
import { AccessTime, PrecisionManufacturing } from "@mui/icons-material";
import {
  Alert,
  AlertTitle,
  Box,
  Container,
  Divider,
  TextField,
} from "@mui/material";
import React, { useRef } from "react";
import { GraphType, NodeType, SetGraphType } from "../../types";
import { updateNode } from "../../utils/graph_utils";

interface NodeEditorProps {
  node?: NodeType;
  setGraph: SetGraphType;
}

// Updates the height of the editor based on its content.
// const updateHeight = () => {
// 	const contentHeight = Math.min(1000, editor.getContentHeight());
// 	container.style.width = `${width}px`;
// 	container.style.height = `${contentHeight}px`;
// 	try {
// 		ignoreEvent = true;
// 		editor.layout({ width, height: contentHeight });
// 	} finally {
// 		ignoreEvent = false;
// 	}
// };

function NodeEditor({ node, setGraph }: NodeEditorProps) {
  const editorRef = useRef(null);

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
    <Box sx={{ my: 2 }}>
      <Alert severity="info">
        <AlertTitle>
          Output <i>(5hrs ago)</i>
        </AlertTitle>
        <Ansi>{node.data.output ?? ""}</Ansi>
      </Alert>
    </Box>
  );

  return (
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
      <Box sx={{ my: 2 }}>
        <Editor
          height="60vh"
          defaultLanguage="python"
          value={node.data.code}
          onChange={(code?: string) => {
            updateNode(node?.id, { data: { code: code } }, setGraph);
          }}
        />
      </Box>
      <Divider></Divider>

      <pre>{cell_output}</pre>
    </Container>
  );
}

export default NodeEditor;
