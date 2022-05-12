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
    with open("test_dag.gnote", 'rb') as f:
        dag = f.read()
        return Response(dag)

@app.post("/save_graph")
def save_graph():
    """Compile & save the dag, returns updated proto (with latest in/out)."""
    return True

@app.get("/run_cell")
def run_cell(cell_id: str):
    """Runs the cell & returns updated cell (with output)"""
    return True

