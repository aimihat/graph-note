from google.protobuf.json_format import MessageToJson
from proto.classes import graph_pb2
from execution.helpers import code_helpers

P1 = graph_pb2.Port(uid="1", name="x_source")
P2 = graph_pb2.Port(uid="2", name="x_input")

# A simple test DAG with 1 cell and 1 dependency.
TEST_CELL = graph_pb2.Cell()
TEST_CELL.uid = "test_cell"
TEST_CELL.code = """x = INPUT["x_input"]
y = x"""
TEST_CELL.in_ports.extend([P2])
TEST_DAG = graph_pb2.Graph()
TEST_DAG.cells.extend([TEST_CELL])
TEST_DAG.connections.extend(
    [
        graph_pb2.Connection(from_port=P1, to_port=P2),
    ]
)
EXPECTED_COMPILED_TEST_CELL = """def test_cell(x_input):
	x = x_input
	y = x
test_cell(x_input=OUT_PORT_VALUES['x_source'])"""

# Same as above, with re-use of the input dependency
TEST_CELL2 = graph_pb2.Cell()
TEST_CELL2.uid = "test_cell"
TEST_CELL2.code = """x = INPUT["x_input"]
y = x
z = INPUT["x_input"]"""
TEST_CELL2.in_ports.extend([P2])
TEST_DAG2 = graph_pb2.Graph()
TEST_DAG2.cells.extend([TEST_CELL2])
TEST_DAG2.connections.extend(
    [
        graph_pb2.Connection(from_port=P1, to_port=P2),
    ]
)
EXPECTED_COMPILED_TEST_CELL2 = """def test_cell(x_input):
	x = x_input
	y = x
	z = x_input
test_cell(x_input=OUT_PORT_VALUES['x_source'])"""


def test_cell_compilation():
    """Checks that a validated cell gets compiled as expected
    i.e. as a function defined with cell inputs as function arguments
    and a function call with the connected outputs."""

    compiled_cell = code_helpers.compile_cell(TEST_DAG, TEST_CELL)
    assert compiled_cell == EXPECTED_COMPILED_TEST_CELL


def test_cell_compilation_with_input_reuse():
    """Checks that a validated cell gets compiled as expected
    when an input is used multiple times in the cell code."""

    compiled_cell = code_helpers.compile_cell(TEST_DAG2, TEST_CELL2)
    assert compiled_cell == EXPECTED_COMPILED_TEST_CELL2
