import uuid

from execution.helpers import code_helpers
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


def detect_out_ports(cell: graph_pb2.Cell):
    """Detects output ports for a cell that has been just executed."""
    ...


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
    connected_inputs = [c.to_port.uid for c in dag.connections]
    if not all(p.uid in connected_inputs for p in cell.in_ports):
        return ValidationResult.DISCONNECTED_INPUT

    # Check that the cell inputs have a runtime value
    in_port_uids = [p.uid for p in cell.in_ports]
    for c in dag.connections:
        if c.to_port.uid in in_port_uids and c.from_port.last_updated == 0:
            return ValidationResult.INPUT_MISSING_RUNTIME_VAL

    return ValidationResult.CAN_BE_EXECUTED


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
