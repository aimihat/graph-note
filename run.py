import asyncio
import logging
from pathlib import Path

import jupyter_client

from graphnote.execution.runner import GraphExecutor
from graphnote.proto.classes import graph_pb2

KERNEL_SPEC_DIR = Path("/Users/aimilioshatzistamou/Library/Jupyter/runtime/")

logging.basicConfig(level=logging.INFO)
client = jupyter_client.BlockingKernelClient()
client.load_connection_file(str(KERNEL_SPEC_DIR / "kernel-36225.json"))
client.start_channels()


def get_cell(graph, cell_id):
    ...


async def main():
    with open("test_notebook/test_dag.gnote", "rb") as f:
        test_graph = graph_pb2.Graph()
        test_graph.ParseFromString(f.read())
    runner = GraphExecutor(client, test_graph)

    await runner.init_kernel()

    await runner.run_root(test_graph.root)

    # assume the cells are in the correct order..
    for cell in test_graph.cells:
        await runner.run_cell(cell)


asyncio.run(main())
