from google.protobuf.json_format import MessageToJson
from execution.helpers.graph_helpers import detect_in_ports, validate_cell
from proto.classes import graph_pb2
from execution.helpers import code_helpers

from google.protobuf.json_format import MessageToJson
from proto.classes import graph_pb2
from execution.helpers import code_helpers
import pytest

@pytest.fixture
def single_cell_dag():
    P1 = graph_pb2.Port(uid="1", name="x_source")
    P2 = graph_pb2.Port(uid="2", name="x_input")
    TEST_CELL = graph_pb2.Cell()
    TEST_CELL.uid = "test_cell"
    TEST_CELL.code = \
    """x = INPUT["x_input"]
    y = x"""
    TEST_CELL.in_ports.extend([P2])
    TEST_DAG = graph_pb2.Graph()
    TEST_DAG.cells.extend([TEST_CELL])
    TEST_DAG.connections.extend(
        [
            graph_pb2.Connection(from_port=P1, to_port=P2),
        ]
    )
    return TEST_DAG

class TestCellValidation:
    def test_cell_validation_updates_in_ports(self, single_cell_dag):
        cell = single_cell_dag.cells[0]

        # Remove cell input port
        del cell.in_ports[:]
        assert len(cell.in_ports) == 0

        # Ensure `validate_cell` recreates inputs
        validate_cell(single_cell_dag, cell)
        assert len(cell.in_ports) == 1
        assert cell.in_ports[0].name == "x_input"
        assert len(cell.in_ports[0].uid) > 0

    def test_cell_validation_fails_for_disconnected_input(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        
        # Delete all DAG connections
        del single_cell_dag.connections[:]
        assert validate_cell(single_cell_dag, cell) == False

    def test_cell_validation_fails_for_disconnected_input2(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        
        # Rename input port so that it doesn't match connection
        cell.in_ports[0].name = "bad_name"
        assert validate_cell(single_cell_dag, cell) == False

    def test_cell_validation_succeed_for_connected_inputs(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        assert validate_cell(single_cell_dag, cell) == True

class TestDetectInPorts:
    def test_detect_in_ports_add_new_port(self, single_cell_dag):
        cell = single_cell_dag.cells[0]

        # Remove cell input port
        del cell.in_ports[:]
        detect_in_ports(cell)
        
        assert len(cell.in_ports) == 1
        assert cell.in_ports[0].name == "x_input"
        assert len(cell.in_ports[0].uid) > 0

    def test_detect_in_ports_doesnt_recreate_existing_ports(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        existing_port = cell.in_ports[0]

        detect_in_ports(cell)

        assert len(cell.in_ports) == 1
        assert cell.in_ports[0].name == existing_port.name
        assert cell.in_ports[0].uid == existing_port.uid
