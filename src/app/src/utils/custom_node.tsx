import React, { memo } from "react";
import { useCallback } from "react";
import { Handle, Position } from "react-flow-renderer";

const handleStyle = { left: 10 };

export default memo(({ data, isConnectable }: any) => {
  let outPortHandles;
  if (data.outputPorts === undefined) {
    outPortHandles = [];
  } else {
    outPortHandles = data.outputPorts.map((port: any, index: number) => {
      return (
        <Handle
          type="source"
          style={{ top: String(20 + (index) * (80-20) / (data.outputPorts.length-1)) + "%" }}
          key={port.uid}
          id={port.uid}
          isConnectable={isConnectable}
          position={Position.Right}
        />
      );
    });
  }

  let inPortHandles;
  if (data.inputPorts === undefined) {
    inPortHandles = [];
  } else {
    inPortHandles = data.inputPorts.map((port: any, index: number) => {
      console.log(port.uid);
      return (
        <Handle
          type="target"
          style={{ top: String(20 + (index) * (80-20) / (data.inputPorts.length-1)) + "%" }}
          key={port.uid}
          id={port.uid}
          isConnectable={isConnectable}
          position={Position.Left}
        />
      );
    });
  }

  // compute cell size based on number of ports
  let maxVerticalPorts = Math.max(
    data.outputPorts.length,
    data.inputPorts.length
  );
  let cellSize = { lineHeight: maxVerticalPorts };

  return (
    <div className="nodeParent">
    <div className="custom-node" style={cellSize}>
      <div className="inputPorts">{inPortHandles}</div>
      <div>{data.label}</div>
      <div className="outputPorts">{outPortHandles}</div>
    </div>
    <div className="nodeFooter">
      Cell status
    </div>
    </div>
  );
});
