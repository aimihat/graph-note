import { useEffect, useMemo, useState } from 'react';
import ReactFlow, { Controls, MiniMap } from 'react-flow-renderer';
import DAGNode from '../utils/custom_node';
import loadGraph from '../utils/load_proto';

import './node.css';


const rfStyle = {
  backgroundColor: '#B8CEFF',
};


const initialNodes: any = [
  {
      "id": "cell_trainer",
      "type": "dagNode",
      "data": {
          "label": "cell_trainer",
          "outputPorts": [
              {
                  "uid": "3",
                  "name": "X_test"
              },
              {
                  "uid": "4",
                  "name": "predicted"
              },
              {
                  "uid": "5",
                  "name": "y_test"
              },
              {
                  "uid": "6",
                  "name": "clf"
              }
          ],
          "inputPorts": [
          ]
      },
      "width": 150,
      "height": 50,
      "position": {
          "x": 200,
          "y": 0
      }
  },
  {
      "id": "cell_visualize",
      "type": "dagNode",
      "targetPosition": 'left',
      "data": {
          "label": "cell_visualize",
          "outputPorts": [],
          "inputPorts": [
              {
                  "uid": "7",
                  "name": "X_test"
              },
              // {
              //     "uid": "8",
              //     "name": "predicted"
              // },
              // {
              //     "uid": "9",
              //     "name": "y_test"
              // },
              // {
              //     "uid": "10",
              //     "name": "clf"
              // }
          ]
      },
      "width": 150,
      "height": 50,
      "position": {
          "x": 400,
          "y": 0
      }
  }
];


const initialEdges: any = [
  {
      "id": "e3-7",
      "sourceHandle": "3",
      "targetHandle": "7",
      "source": "cell_trainer",
      "target": "cell_visualize"
  },
  // {
  //     "id": "4",
  //     "sourceHandle": "4",
  //     "targetHandle": "8",
  //     "source": "cell_trainer",
  //     "target": "cell_visualize"
  // },
  // {
  //     "id": "5",
  //     "sourceHandle": "5",
  //     "targetHandle": "9",
  //     "source": "cell_trainer",
  //     "target": "cell_visualize"
  // },
  // {
  //     "id": "6",
  //     "sourceHandle": "6",
  //     "targetHandle": "10",
  //     "source": "cell_trainer",
  //     "target": "cell_visualize"
  // }
];

const nodeTypes = {
  dagNode: DAGNode,
};

function Flow() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  useEffect(() => {
    loadGraph(setNodes, setEdges);
  }, [])
  
  return (<ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes}       style={rfStyle} fitView >
          <MiniMap/>
      <Controls />
    </ReactFlow>);
}

export default Flow;