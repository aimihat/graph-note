from typing import Dict
import uuid
import json

import execution.runner as runner
import execution.helpers.code_helpers as code_helpers
from execution.messages import definitions, parsers
from proto.classes import graph_pb2
import enum


def detect_in_ports(cell: graph_pb2.Cell) -> None:
    """Detects input ports for the cell. Updates the cell's ports."""
    # TODO: cache based on cell name and code hash.

    # Detect input ports.
    cell_inputs = code_helpers.detect_tag(cell.code, code_helpers.INPUT_VAR_TAG)

    # Keep existing ports (to preserve port ids) & add new ports.
    existing_ports = list(cell.in_ports)
    del cell.in_ports[:]
    cell.in_ports.extend([port for port in existing_ports if port.name in cell_inputs])
    cell.in_ports.extend(
        [
            graph_pb2.Port(uid=str(uuid.uuid4()), name=in_)
            for in_ in cell_inputs
            if in_ not in [p.name for p in cell.in_ports]
        ]
    )


def update_out_ports(
    executor_state: runner.GraphExecutorState, cell: graph_pb2.Cell, msg: Dict
) -> None:
    """Updates the output ports of a cell after executing it.

    After executing a cell we ping the kernel for the latest cell metadata.
    This produces a std-out msg that can be compared to the previous timestep.
    """

    parsed_message = parsers.parse_message(msg)
    if type(parsed_message.content) == definitions.CellStdout:
        if executor_state.cell_exec_success[cell.uid] == False:
            # Do not update ports if the cell failed to full execute.
            return

        prev_metadata = executor_state.out_port_metadata

        # parse the current port metadata from msg
        meta_str = parsed_message.content.text
        meta_dict = json.loads(meta_str)

        # compute the diff & update cell output ports (keeping existing)
        detected_outputs = [
            {"name": k, "last_updated": v}
            for k, v in meta_dict.items()
            if (k not in prev_metadata.keys() or prev_metadata[k] != meta_dict[k])
        ]

        new_ports = []
        existing_port_names = [p_.name for p_ in cell.out_ports]

        for p in detected_outputs:
            # if output exists re-use the same port - as it may have associated connections
            if p["name"] in existing_port_names:
                existing_port = cell.out_ports[existing_port_names.index(p["name"])]
                existing_port.last_updated = p["last_updated"]
                new_ports.append(existing_port)
            else:
                new_ports.append(
                    graph_pb2.Port(
                        uid=str(uuid.uuid4()),
                        name=p["name"],
                        last_updated=p["last_updated"],
                    )
                )

        del cell.out_ports[:]
        cell.out_ports.extend(new_ports)
        # update previous metadata
        executor_state.out_port_metadata = meta_dict


def reset_out_ports(graph: graph_pb2.Graph) -> None:
    """Resets all output ports in the graph to have no runtime value."""
    for cell in graph.cells:
        for port in cell.out_ports:
            port.last_updated = 0


def validate_root(root: graph_pb2.Cell) -> bool:
    return True  # TODO


class ValidationResult(enum.Enum):
    CAN_BE_EXECUTED = 0
    DISCONNECTED_INPUT = 1
    INPUT_MISSING_RUNTIME_VAL = 2


def validate_cell(dag: graph_pb2.Graph, cell: graph_pb2.Cell) -> ValidationResult:
    """Validates that a cell is able to be executed."""

    # Ensure input ports are up-to-date.
    detect_in_ports(cell)

    # TODO: prune connections before checking for validity.
    # Check that the cell's input ports are connected. Disconnected outputs can be ignored.
    connected_inputs = [c.target_uid for c in dag.connections]
    if not all(p.uid in connected_inputs for p in cell.in_ports):
        return ValidationResult.DISCONNECTED_INPUT

    # Check that the cell inputs have a runtime value
    in_port_uids = [p.uid for p in cell.in_ports]
    port_mapping = graph_port_mapping(dag)
    for c in dag.connections:
        if (
            c.target_uid in in_port_uids
            and port_mapping[c.source_uid].last_updated == 0
        ):
            return ValidationResult.INPUT_MISSING_RUNTIME_VAL

    return ValidationResult.CAN_BE_EXECUTED


def graph_port_mapping(graph: graph_pb2.Graph) -> Dict[str, graph_pb2.Port]:
    """Returns a mapping from uid->port."""
    # TODO: cache
    port_map = {}
    for cell in graph.cells:
        for p in list(cell.in_ports) + list(cell.out_ports):
            port_map[p.uid] = p
    return port_map


# @Future


def prune_connections():
    """Removes unused connections (e.g. deleted ports / cells)."""
    ...


def is_valid():
    """Asserts that the entire DAG can be executed."""
    ...


def get_cell_dependencies(cell: graph_pb2.Cell):
    """Returns the cells which must be executed directly before cell (1-step deps)."""
    ...


def iter():
    """Returns cells in accordance with the execution dependency graph."""
    ...
