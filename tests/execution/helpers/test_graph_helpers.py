from copy import deepcopy
from google.protobuf.json_format import MessageToJson
from execution.helpers.graph_helpers import (
    detect_in_ports,
    reset_out_ports,
    validate_cell,
)
from proto.classes import graph_pb2
from execution.helpers import code_helpers

from google.protobuf.json_format import MessageToJson
from google.protobuf import timestamp_pb2
from proto.classes import graph_pb2
from execution.helpers import code_helpers
import pytest
import time


@pytest.fixture
def single_cell_dag():
    TEST_CELL = graph_pb2.Cell()
    TEST_CELL.uid = "test_cell"
    TEST_CELL.code = """x = INPUT["x_input"]
    y = x"""

    # Input ports
    P1 = graph_pb2.Port(uid="1", name="x_source")
    P2 = graph_pb2.Port(uid="2", name="x_input")
    TEST_CELL.in_ports.extend([P2])
    # Output ports
    P3 = graph_pb2.Port(uid="3", name="out1", last_updated=int(time.time()))
    P4 = graph_pb2.Port(uid="4", name="out2")
    TEST_CELL.out_ports.extend([P3, P4])

    TEST_DAG = graph_pb2.Graph()
    TEST_DAG.cells.extend([TEST_CELL])
    TEST_DAG.connections.extend(
        [
            graph_pb2.Connection(from_port=P1, to_port=P2),
        ]
    )
    return TEST_DAG


class TestCellValidation:
    def test_updates_in_ports(self, single_cell_dag):
        cell = single_cell_dag.cells[0]

        # Remove cell input port
        del cell.in_ports[:]
        assert len(cell.in_ports) == 0

        # Ensure `validate_cell` recreates inputs
        validate_cell(single_cell_dag, cell)
        assert len(cell.in_ports) == 1
        assert cell.in_ports[0].name == "x_input"
        assert len(cell.in_ports[0].uid) > 0

    def test_fails_for_disconnected_input(self, single_cell_dag):
        cell = single_cell_dag.cells[0]

        # Delete all DAG connections
        del single_cell_dag.connections[:]
        assert validate_cell(single_cell_dag, cell) == False

    def test_fails_for_disconnected_input2(self, single_cell_dag):
        cell = single_cell_dag.cells[0]

        # Rename input port so that it doesn't match connection
        cell.in_ports[0].name = "bad_name"
        assert validate_cell(single_cell_dag, cell) == False

    def test_succeed_for_connected_inputs(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        assert validate_cell(single_cell_dag, cell) == True

    def test_fails_if_input_missing_runtime_value(self):
        ...

    def test_fails_for_input_without_runtime_value(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        del cell.in_ports[:]
        assert len(cell.in_ports) == 0
        cell.code = cell.code.replace("INPUT", "")

        assert validate_cell(single_cell_dag, cell) == True

    def test_succeeds_if_no_inputs(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        del cell.in_ports[:]
        assert len(cell.in_ports) == 0
        cell.code = cell.code.replace("INPUT", "")

        assert validate_cell(single_cell_dag, cell) == True


class TestDetectInPorts:
    def test_adds_new_port(self, single_cell_dag):
        cell = single_cell_dag.cells[0]

        # Remove cell input port
        del cell.in_ports[:]
        detect_in_ports(cell)

        assert len(cell.in_ports) == 1
        assert cell.in_ports[0].name == "x_input"
        assert len(cell.in_ports[0].uid) > 0

    def test_doesnt_recreate_existing_ports(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        existing_port = cell.in_ports[0]

        detect_in_ports(cell)

        assert len(cell.in_ports) == 1
        assert cell.in_ports[0].name == existing_port.name
        assert cell.in_ports[0].uid == existing_port.uid


class TestResetOutPorts:
    def test_output_ports_reset(self, single_cell_dag):
        all_ports = [p for cell in single_cell_dag.cells for p in cell.out_ports]
        assert not all(p.last_updated == 0 for p in all_ports)
        reset_out_ports(single_cell_dag)
        assert all(p.last_updated == 0 for p in all_ports)

    def test_empty_ports_remain_empty(self, single_cell_dag):
        empty_ports = [
            p
            for cell in single_cell_dag.cells
            for p in cell.out_ports
            if p.last_updated == 0
        ]
        reset_out_ports(single_cell_dag)
        assert all(p.last_updated == 0 for p in empty_ports)

    def test_does_not_corrupt_dag(self, single_cell_dag):
        input_dag = deepcopy(single_cell_dag)
        reset_out_ports(single_cell_dag)

        # Outputs can be affected
        for cell in input_dag.cells:
            del cell.out_ports[:]
        for cell in single_cell_dag.cells:
            del cell.out_ports[:]

        assert single_cell_dag.SerializeToString(
            deterministic=True
        ) == input_dag.SerializeToString(deterministic=True)
