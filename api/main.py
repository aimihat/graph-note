# MVP for what the UI-backend interface could look like.

"""
GET /dag -> returns updated proto.
POST /save (dag) -> compile & save the dag, returns updated proto (with latest in/out)
POST /run_cell (cell_id) -> runs the cell & returns updated cell (with output).

future: run full dag, with websocket updates.
"""

from typing import Optional

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

import asyncio
import logging
from pathlib import Path

import jupyter_client

from execution.runner import GraphExecutor
from proto.classes import graph_pb2

KERNEL_SPEC_DIR = Path(__file__).parent.parent.parent / ".kernelspecs"
CONNECT_FILE_PATH = KERNEL_SPEC_DIR / Path("kernel.json")

logging.basicConfig(level=logging.INFO)
client = jupyter_client.BlockingKernelClient()
client.load_connection_file(str(CONNECT_FILE_PATH))
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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,  # TODO: remove
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/read_graph")
def read_graph():
    """Returns the serialised graph."""
    with open("test_dag.gnote", "rb") as f:
        dag = f.read()
        return Response(dag)


@app.post("/save_graph")
def save_graph():
    """Compile & save the dag, returns updated proto (with latest in/out)."""
    with open("test_dag.gnote", "rb") as f:
        dag = f.read()
        return Response(dag)


@app.get("/run_cell")
def run_cell(cell_id: str):
    """Runs the cell & returns updated cell (with output)"""
    return True
