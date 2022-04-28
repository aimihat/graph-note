import jupyter_client
import dataclasses
from pathlib import Path

CELL_DIR = Path(__file__).parent.parent / 'cells'
print(CELL_DIR, CELL_DIR.parent, CELL_DIR.parent.parent)
KERNEL_SPEC_DIR = Path("/Users/aimilioshatzistamou/Library/Jupyter/runtime/")

client = jupyter_client.BlockingKernelClient()

# Get connection info
client.load_connection_file(KERNEL_SPEC_DIR / "kernel-69224.json")
client.start_channels()

@dataclasses.dataclass
class Node:
    filepath: str

    def load_code(self):
        with open(self.filepath, 'r') as f:
            return f.read()

dag = [
    Node(CELL_DIR / "node_root.py"),
    Node(CELL_DIR / "node_data.py"),
    Node(CELL_DIR / "node_trainer.py"),
    Node(CELL_DIR / "node_visualize.py"),
]

# Execute dag
for node in dag:
    print(f"Executing {node.filepath}")
    reply_msg = client.execute(node.load_code())
    reply = client.get_shell_msg()
    print(reply)