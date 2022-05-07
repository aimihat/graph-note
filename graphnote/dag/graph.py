import dataclasses
from typing import List

from graphnote.dag.cells import Cell, Connection, Port, Root

PortName = str


@dataclasses.dataclass
class Dagbook:
    root: Root  # imports
    cells: List[Cell]  # vertices
    connections: List[Connection]  # edges
    # TODO: change this to hold protobuf instance

    def compile(self) -> None:
        """Compiles every cell in the DAG."""
        for c in self.cells:
            c.compile()

    def prune_connections(self):
        """Removes unused connections (e.g. deleted ports / cells)."""
        ...

    def get_connected_ports(self):
        connected_ports = []
        for c in self.connections:
            connected_ports += [c.from_port, c.to_port]
        return connected_ports

    def is_valid(self):
        """Asserts that the entire DAG can be executed."""

        for c in self.cells:
            if not self.cell_is_valid(c):
                return False
        return True

    def root_is_valid(self, root: Root) -> bool:
        return True  # TODO

    def cell_is_valid(self, cell: Cell) -> bool:
        """Assert that the cell's input ports are connected. Disconnected outputs can be ignored."""
        assert cell.input_vars is not None
        # TODO: only compute when conns change?
        connected_ports = self.get_connected_ports()

        input_ports = [Port(cell.uid, in_) for in_ in cell.input_vars]
        if len(input_ports) == 0:
            return True

        print([p for p in input_ports if p not in connected_ports])
        return all(p in connected_ports for p in input_ports)

    def get_cell_dependencies(self, cell: Cell):
        """Returns the cells which must be executed directly before cell (1-step deps)."""
        assert cell.input_vars is not None
        in_ports = [Port(cell.uid, in_) for in_ in cell.input_vars]
        out_port_dependencies = [
            c.from_port for c in self.connections if c.to_port in in_ports
        ]
        return [p.cell_uid for p in out_port_dependencies]

    def iter(self):
        """Returns cells in accordance with the execution dependency graph."""

        cells_to_execute = list(self.cells)
        cells_executed = []

        while len(cells_to_execute):
            cell_to_execute = None
            for c in cells_to_execute:
                # Check if all dependencies have been evaluated
                can_be_run = all(
                    cell_dependency in cells_executed
                    for cell_dependency in self.get_cell_dependencies(c)
                )

                if can_be_run:
                    cell_to_execute = c
                    break

            if cell_to_execute is None:
                raise Exception("No cell could be executed.")

            # Execute the cell and mark as executed
            cells_executed.append(c.uid)
            cells_to_execute.remove(c)
            yield c
