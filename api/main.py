# MVP for what the UI-backend interface could look like.

"""
GET /dag -> returns updated proto.
POST /save (dag) -> compile & save the dag, returns updated proto (with latest in/out)
POST /run_cell (cell_id) -> runs the cell & returns updated cell (with output).

future: run full dag, with websocket updates.
"""

from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from execution.helpers.graph_helpers import detect_in_ports
from execution.kernel.launcher import CONNECT_FILE_PATH
import logging
import base64
from .types import RequestBodyGraph, APIResponses

logger = logging.getLogger()
app = FastAPI()

import asyncio

import jupyter_client
from execution.runner import GraphExecutor
from proto.classes import graph_pb2

client = jupyter_client.BlockingKernelClient()
client.load_connection_file(str(CONNECT_FILE_PATH))
client.start_channels()


DAGBOOK_PATH = "examples/test_dag.gnote"

# Initialize the graph runner.
with open(DAGBOOK_PATH, "rb") as f:
    test_graph = graph_pb2.Graph()
    test_graph.ParseFromString(f.read())
    runner = GraphExecutor(client, test_graph)

# Prepare the kernel for execution.
asyncio.run(runner.initialize())
asyncio.run(runner.run_root(test_graph.root))


origins = ["*"]

app.add_middleware(
    CORSMiddleware,  # TODO: remove
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/read_graph")
def read_graph(response: Response):
    """Returns the serialised graph."""
    response.status_code = APIResponses.UpdatedGraph.value
    return Response(runner.dag.SerializeToString())


@app.post("/save_graph")
def save_graph(body: RequestBodyGraph, response: Response):
    """Compile & save the dag, returns updated proto (with latest in/out)."""

    req_graph = graph_pb2.Graph()
    graph_bytes = base64.b64decode(body.b64_graph)
    req_graph.ParseFromString(graph_bytes)

    for cell in req_graph.cells:
        detect_in_ports(cell)

    # TODO: actually save the updated DAG and not just update state.
    runner.dag = req_graph
    response.status_code = APIResponses.UpdatedGraph.value
    return Response(req_graph.SerializeToString())


@app.get("/run_cell")
async def run_cell(cell_uid: str, response: Response):
    """Runs the cell & returns updated cell (with output)"""

    for cell in runner.dag.cells:
        if cell.uid == cell_uid:
            try:
                await runner.run_cell(cell)
            except Exception as e:
                print(f"Could not execute due to error: {e}")
                return PlainTextResponse(
                    str(e),
                    status_code=APIResponses.ErrorMessage.value,
                )

    response.status_code = APIResponses.UpdatedGraph.value
    return Response(runner.dag.SerializeToString())
