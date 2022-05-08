import dataclasses
import imp
import uuid
from typing import List

from proto.classes import graph_pb2

from graphnote.execution import code_helpers
from graphnote.execution.cells import Cell, Connection, Port, Root

INPUT_VAR_TAG = "INPUT"
OUTPUT_VAR_TAG = "OUTPUT"


def detect_in_ports(cell):
    """Detects input ports for the cell. Updates the cell's ports."""
    # TODO: cache based on cell name and code hash.

    # Detect input ports.
    cell_inputs = code_helpers.parse_tag(cell.code, INPUT_VAR_TAG)
    # Keep existing ports (to preserve port ids) & add new ports.
    cell.in_ports[:] = [port for port in cell.in_ports if port.name in cell_inputs]
    cell.in_ports.extend(
        [
            graph_pb2.Port(id=uuid.uuid4(), name=in_)
            for in_ in cell_inputs
            if in_ not in [p.name for p in cell.in_ports]
        ]
    )


def detect_out_ports(cell):
    """Detects output ports for a cell that has been just executed."""
    ...


def validate_root(root: graph_pb2.Cell) -> bool:
    return True  # TODO


def validate_cell(dag: graph_pb2.Graph, cell: graph_pb2.Cell) -> bool:
    """Assert that the cell's input ports are connected. Disconnected outputs can be ignored."""

    # Ensure ports are up-to-date.
    detect_in_ports(dag, cell)

    if len(cell.in_ports) == 0:
        return True

    # TODO: prune connections before checking for validity.
    connected_inputs = [c.to_port.id for c in dag.connections]
    return all(p.id in connected_inputs for p in cell.in_ports)


# @Future


def prune_connections(self):
    """Removes unused connections (e.g. deleted ports / cells)."""
    ...


def is_valid(self):
    """Asserts that the entire DAG can be executed."""
    ...


def get_cell_dependencies(self, cell: Cell):
    """Returns the cells which must be executed directly before cell (1-step deps)."""
    ...


def iter(self):
    """Returns cells in accordance with the execution dependency graph."""
    ...
