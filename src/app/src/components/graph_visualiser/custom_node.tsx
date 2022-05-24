import { memo } from "react";
import { Handle, HandleType, Position } from "react-flow-renderer";
import { NodeDataType, PortType } from "../../types";

interface CustomNodeProps {
  id: string;
  data: NodeDataType;
}

interface CustomHandleProps {
  type: HandleType;
  numSameTypePorts?: number;
  order: number;
  port: PortType;
  position: Position;
}

function CustomHandle({
  type,
  numSameTypePorts,
  port,
  order,
  position,
}: CustomHandleProps) {
  let topPosition = 0;
  if (numSameTypePorts !== undefined) {
    topPosition = 20 + (order * (80 - 20)) / (numSameTypePorts - 1);
  }

  return (
    <Handle
      type={type}
      style={{ top: String(topPosition) + "%" }}
      id={port.uid}
      isConnectable={true}
      position={position}
    />
  );
}

export default memo(({ id, data }: CustomNodeProps) => {
  let numOutputPorts = data.outputPorts?.length;
  let outPortHandles = data.outputPorts?.map(
    (port: PortType, index: number) => {
      return (
        <CustomHandle
          type="source"
          key={port.uid}
          numSameTypePorts={numOutputPorts}
          port={port}
          position={Position.Right}
          order={index}
        />
      );
    }
  );

  let numInputPorts = data.inputPorts?.length;
  let inPortHandles = data.inputPorts?.map((port: any, index: number) => {
    return (
      <CustomHandle
        type="target"
        key={port.uid}
        port={port}
        numSameTypePorts={numInputPorts}
        position={Position.Left}
        order={index}
      />
    );
  });

  // compute cell size based on number of ports
  let maxVerticalPorts = Math.max(numInputPorts ?? 0, numOutputPorts ?? 0);
  let cellSize = { lineHeight: maxVerticalPorts };

  return (
    <div className="nodeParent">
      <div className="custom-node" style={cellSize}>
        <div className="inputPorts">{inPortHandles}</div>
        <div>{id}</div>
        <div className="outputPorts">{outPortHandles}</div>
      </div>
      <div className="nodeFooter">Cell status</div>
    </div>
  );
});
