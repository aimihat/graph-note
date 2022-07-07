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
import { NodeType, SetGraphType } from "../../types";
import { updateNode } from "../../utils/graph_utils";

interface NodeEditorProps {
  node?: NodeType;
  setGraph: SetGraphType;
  setSelectedNodeId: (id: string) => void;
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


function NodeEditor({ node, setGraph, setSelectedNodeId }: NodeEditorProps) {
  const editorRef = useRef(null);

  // No cell selected.
  if (node === undefined) {
    return (
      <Box sx={{ my: 2, mx: 2 }}>
        <h3>Select or create a node</h3>
      </Box>
    );
  }

  function handleEditorDidMount(editor: any, monaco: any) {
    // here is the editor instance
    // you can store it in `useRef` for further usage
    editorRef.current = editor; 

    const updateHeight = () => {
      const contentHeight = Math.min(100, editor.getContentHeight());
      console.log(editor);
      try {
        editor.layout({ width: "100%", height: contentHeight });
      } finally {
      }
    };
    editor.onDidContentSizeChange(updateHeight);
    updateHeight();

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
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
            updateNode(node?.id, {id: event.target.value}, setGraph);
            setSelectedNodeId(event.target.value);
          }}
        />
      </Box>
      <Box sx={{ my: 2 }}>
        <Editor
          // height="60vh"
          defaultLanguage="python"
          value={node.data.code}
          onChange={(code?: string) => {
            updateNode(node?.id, {data: {code: code}}, setGraph)
          }}
          onMount={handleEditorDidMount}

        />
      </Box>
      <Divider></Divider>
      <pre>{cell_output}</pre>
    </Container>
  );
}

export default NodeEditor;
