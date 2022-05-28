import dataclasses
import imp
import uuid
from typing import List

from graphnote.execution.helpers import code_helpers
from graphnote.proto.classes import graph_pb2

INPUT_VAR_TAG = "INPUT"
OUTPUT_VAR_TAG = "OUTPUT"


def detect_in_ports(cell: graph_pb2.Cell) -> None:
    """Detects input ports for the cell. Updates the cell's ports."""
    # TODO: cache based on cell name and code hash.

    # Detect input ports.
    cell_inputs = code_helpers.detect_tag(cell.code, INPUT_VAR_TAG)

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


def validate_root(root: graph_pb2.Cell) -> bool:
    return True  # TODO


def validate_cell(dag: graph_pb2.Graph, cell: graph_pb2.Cell) -> bool:
    """Assert that the cell's input ports are connected. Disconnected outputs can be ignored."""

    # Ensure ports are up-to-date.
    detect_in_ports(cell)

    if len(cell.in_ports) == 0:
        return True

    # TODO: prune connections before checking for validity.
    connected_inputs = [c.to_port.uid for c in dag.connections]
    print(
        connected_inputs,
        all(p.uid in connected_inputs for p in cell.in_ports),
        cell.in_ports,
    )
    return all(p.uid in connected_inputs for p in cell.in_ports)


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
