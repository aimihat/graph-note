import React, { memo } from 'react';
import { useCallback } from "react";
import { Handle, Position } from "react-flow-renderer";

const handleStyle = { left: 10 };

export default memo(({ data, isConnectable }: any) => {

  let outPortHandles;
  if (data.outputPorts === undefined) {
    outPortHandles = [];
  } else {
    outPortHandles = data.outputPorts.map((port: any, index: number) => {
      console.log(port.uid);
      return <Handle type="source" style={{ top: 10 * index}} key={port.uid} id={port.uid} isConnectable={isConnectable} position={Position.Right} />
  });
  }

  let inPortHandles;
  if (data.inputPorts === undefined) {
    inPortHandles = [];
  } else {
    inPortHandles = data.inputPorts.map((port: any, index: number) => {
      console.log(port.uid);
      return <Handle type="target" style={{ top: 10 * index}} key={port.uid} id={port.uid} isConnectable={isConnectable} position={Position.Left} />
  });
  }

  return (
    <div className="custom-node">
      {inPortHandles}
      <div>
      {data.label}
      </div>
      {outPortHandles}
    </div>
  );
});
