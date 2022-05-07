# MVP for what the UI-backend interface could look like.

"""
GET /dag -> returns updated proto.
POST /save (dag) -> compile & save the dag, returns updated proto (with latest in/out)
POST /run_cell (cell_id) -> runs the cell & returns updated cell (with output).
"""
