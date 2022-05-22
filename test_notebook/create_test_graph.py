import sys
from pathlib import Path

from google.protobuf.json_format import MessageToJson

sys.path.append("../")
from src.proto.classes import graph_pb2

CELL_DIR = Path(__file__).parent / "test_cells"


def read_cell(f_path):
    with open(f_path, "r") as f:
        return f.read()


# Create cells
cell_root = graph_pb2.Cell()
cell_root.uid = "cell_root"
cell_root.code = read_cell(CELL_DIR / "cell_root.py")

cell_data = graph_pb2.Cell()
cell_data.uid = "cell_data"
cell_data.code = read_cell(CELL_DIR / "cell_data.py")
cell_data.out_ports.extend(
    [graph_pb2.Port(uid="1", name="digits__different_name")]
)  # can connect out-in with different names

cell_trainer = graph_pb2.Cell()
cell_trainer.uid = "cell_trainer"
cell_trainer.code = read_cell(CELL_DIR / "cell_trainer.py")
cell_trainer.in_ports.extend([graph_pb2.Port(uid="2", name="digits")])
cell_trainer.out_ports.extend(
    [
        graph_pb2.Port(uid="3", name="X_test"),
        graph_pb2.Port(uid="4", name="predicted"),
        graph_pb2.Port(uid="5", name="y_test"),
        graph_pb2.Port(uid="6", name="clf"),
    ]
)
cell_trainer.output = "This is the output for the trainer cell."

cell_visualize = graph_pb2.Cell()
cell_visualize.uid = "cell_visualize"
cell_visualize.code = read_cell(CELL_DIR / "cell_visualize.py")
cell_visualize.in_ports.extend(
    [
        graph_pb2.Port(uid="7", name="X_test"),
        graph_pb2.Port(uid="8", name="predicted"),
        graph_pb2.Port(uid="9", name="y_test"),
        graph_pb2.Port(uid="10", name="clf"),
    ]
)

# Create connections
connections = [
    graph_pb2.Connection(
        from_port=cell_data.out_ports[0], to_port=cell_trainer.in_ports[0]
    ),
]
for from_, to_ in zip(cell_trainer.out_ports, cell_visualize.in_ports):
    connections.append(graph_pb2.Connection(from_port=from_, to_port=to_))

# Create dag
dag = graph_pb2.Graph()
dag.cells.extend([cell_data, cell_trainer, cell_visualize])
dag.root.CopyFrom(cell_root)
dag.connections.extend(connections)

# Write the new dag back to disk.
f = open("test_dag.gnote", "wb")
f.write(dag.SerializeToString())
f.close()

# For debugging purposes, save as json also

json_obj = MessageToJson(dag)
f = open("test_dag.json", "w")
f.write(json_obj)
f.close()
