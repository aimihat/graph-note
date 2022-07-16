from copy import deepcopy
from unittest.mock import patch
import uuid
from execution.helpers.graph_helpers import (
    ValidationResult,
    detect_in_ports,
    graph_port_mapping,
    reset_out_ports,
    update_out_ports,
    validate_cell,
)
from proto.classes import graph_pb2

from proto.classes import graph_pb2
import pytest
import json


@pytest.fixture
def executor_state():
    state_step_1 = {"out_port_metadata": {"out1": 99, "out2": 99}}

    state_step_2 = {"out_port_metadata": {"out1": 100, "out2": 100}}

    return (state_step_1, state_step_2)


def executor_state_to_meta_msg(state):
    return {
        "header": {},
        "msg_id": {},
        "msg_type": "stream",
        "parent_header": {},
        "metadata": {},
        "content": {
            "name": "stdout",
            "text": json.dumps(state["out_port_metadata"]),
        },
    }


@pytest.fixture
def source_port():
    P1 = graph_pb2.Port(uid="1", name="x_source", last_updated=99)
    return P1


@pytest.fixture
def single_cell_dag(source_port):
    TEST_CELL = graph_pb2.Cell()
    TEST_CELL.uid = "test_cell"
    TEST_CELL.code = """x = INPUT["x_input"]
    y = x"""

    # Input ports
    P2 = graph_pb2.Port(uid="2", name="x_input")
    TEST_CELL.in_ports.extend([P2])
    # Output ports
    P3 = graph_pb2.Port(uid="3", name="out1", last_updated=99)
    P4 = graph_pb2.Port(uid="4", name="out2", last_updated=99)
    TEST_CELL.out_ports.extend([P3, P4])

    TEST_DAG = graph_pb2.Graph()
    TEST_DAG.cells.extend([TEST_CELL])
    TEST_DAG.connections.extend(
        [
            graph_pb2.Connection(source_uid=source_port.uid, target_uid=P2.uid),
        ]
    )
    return TEST_DAG


@pytest.fixture
def patched_graph_port_mapping(source_port):
    def patch(graph: graph_pb2.Graph):
        mapping = graph_port_mapping(graph)
        P1 = source_port
        mapping[P1.uid] = P1
        return mapping

    return patch


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
        assert (
            validate_cell(single_cell_dag, cell) == ValidationResult.DISCONNECTED_INPUT
        )

    def test_fails_for_disconnected_input2(self, single_cell_dag):
        cell = single_cell_dag.cells[0]

        # Rename input port so that it doesn't match connection
        cell.in_ports[0].name = "bad_name"
        assert (
            validate_cell(single_cell_dag, cell) == ValidationResult.DISCONNECTED_INPUT
        )

    def test_succeeds_for_connected_inputs(
        self, single_cell_dag, patched_graph_port_mapping
    ):
        cell = single_cell_dag.cells[0]
        with patch(
            "execution.helpers.graph_helpers.graph_port_mapping",
            side_effect=patched_graph_port_mapping,
        ):
            assert (
                validate_cell(single_cell_dag, cell) == ValidationResult.CAN_BE_EXECUTED
            )

    def test_fails_for_connected_input_without_runtime_value(
        self, single_cell_dag, patched_graph_port_mapping
    ):
        cell = single_cell_dag.cells[0]

        # Set cell's ins to have no runtime value
        port_mapping = patched_graph_port_mapping(single_cell_dag)
        for c in single_cell_dag.connections:
            if c.target_uid in [p.uid for p in cell.in_ports]:
                port_mapping[c.source_uid].last_updated = 0

        with patch(
            "execution.helpers.graph_helpers.graph_port_mapping",
            side_effect=patched_graph_port_mapping,
        ):
            assert (
                validate_cell(single_cell_dag, cell)
                == ValidationResult.INPUT_MISSING_RUNTIME_VAL
            )

    def test_succeeds_if_no_inputs(self, single_cell_dag):
        cell = single_cell_dag.cells[0]
        del cell.in_ports[:]
        assert len(cell.in_ports) == 0
        cell.code = cell.code.replace("INPUT", "")

        assert validate_cell(single_cell_dag, cell) == ValidationResult.CAN_BE_EXECUTED


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


class TestUpdateOutPorts:
    def test_updates_metadata(self, single_cell_dag, executor_state):
        cell = single_cell_dag.cells[0]
        state_step_1, state_step_2 = executor_state
        stdout_metadata_msg = executor_state_to_meta_msg(state_step_2)
        update_out_ports(state_step_1, cell, stdout_metadata_msg)
        assert state_step_1["out_port_metadata"] == state_step_2["out_port_metadata"]

    def test_removes_deleted_ports(self, single_cell_dag, executor_state):
        cell = single_cell_dag.cells[0]
        cell.out_ports.extend(
            [graph_pb2.Port(uid=str(uuid.uuid4()), last_updated=1, name="unused-port")]
        )

        n_ports = len(cell.out_ports)
        state_step_1, state_step_2 = executor_state
        stdout_metadata_msg = executor_state_to_meta_msg(state_step_2)
        update_out_ports(state_step_1, cell, stdout_metadata_msg)
        assert len(cell.out_ports) == n_ports - 1

    def test_adds_new_ports_with_correct_timestamp(
        self, single_cell_dag, executor_state
    ):
        cell = single_cell_dag.cells[0]
        del cell.out_ports[1:]
        assert len(cell.out_ports) == 1
        state_step_1, state_step_2 = executor_state
        stdout_metadata_msg = executor_state_to_meta_msg(state_step_2)
        update_out_ports(state_step_1, cell, stdout_metadata_msg)
        assert len(cell.out_ports) == 2
        assert all(
            p.last_updated == state_step_2["out_port_metadata"][p.name]
            for p in cell.out_ports
        )

    def test_does_not_duplicate_ports(self, single_cell_dag, executor_state):
        # ensure ports in connections map to the same objects
        cell = single_cell_dag.cells[0]
        single_cell_dag.connections.extend(
            [
                graph_pb2.Connection(
                    source_uid=cell.out_ports[0].uid, target_uid="test_port_uid"
                ),
            ]
        )

        state_step_1, state_step_2 = executor_state
        print("step 1", single_cell_dag)
        stdout_metadata_msg = executor_state_to_meta_msg(state_step_2)
        update_out_ports(state_step_1, cell, stdout_metadata_msg)
        print("step 2", single_cell_dag)
        port_mapping = graph_port_mapping(single_cell_dag)
        assert (
            port_mapping[single_cell_dag.connections[-1].source_uid].last_updated == 100
        )

    def test_does_not_update_if_metadata_unchanged(
        self, single_cell_dag, executor_state
    ):
        cell = single_cell_dag.cells[0]
        state_step_1, _ = executor_state
        stdout_metadata_msg = executor_state_to_meta_msg(state_step_1)
        ports_pre_updated = cell.out_ports
        update_out_ports(state_step_1, cell, stdout_metadata_msg)
        assert cell.out_ports == ports_pre_updated


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
