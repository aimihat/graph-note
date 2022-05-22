import Editor from "@monaco-editor/react";
import { AccessTime } from "@mui/icons-material";
import {
  Alert,
  AlertTitle,
  Box,
  Container,
  Divider,
  TextField,
} from "@mui/material";
import { NodeType } from "../../types";

interface NodeEditorProps {
  node?: NodeType;
  updateNodeCode: (code?: string) => void;
  updateNodeId: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

function NodeEditor({ node, updateNodeCode, updateNodeId }: NodeEditorProps) {
  // No cell selected.
  if (node === undefined) {
    return (
      <Box sx={{ my: 2, mx: 2 }}>
        <h3>Select or create a node</h3>
      </Box>
    );
  }

  // Display cell output.
  let cell_output = <></>;
  if (node.data.output) {
    cell_output = (
      <Box sx={{ my: 2 }}>
        <Alert severity="info">
          <AlertTitle>
            Output <i>(5hrs ago)</i>
          </AlertTitle>
          {node.data.output}
        </Alert>
      </Box>
    );
  }

  return (
    <Container>
      <Box paddingY={2}>
        <TextField
          id="node-id"
          label="Node name"
          variant="outlined"
          size="small"
          value={node.id}
          onChange={updateNodeId}
        />
      </Box>
      <Box sx={{ my: 2 }}>
        <Editor
          height="60vh"
          defaultLanguage="python"
          value={node.data.code}
          onChange={updateNodeCode}
        />
      </Box>
      <Divider></Divider>
      {cell_output}
    </Container>
  );
}

export default NodeEditor;
