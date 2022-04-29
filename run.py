import asyncio
from pathlib import Path

from graphnote.client import GraphRunner
from graphnote.dag import cells

CELL_DIR = Path(__file__).parent / "cells"


async def main():
    dag = [
        cells.Cell(CELL_DIR / "node_root.py"),
        cells.Cell(CELL_DIR / "node_data.py"),
        cells.Cell(CELL_DIR / "node_trainer.py"),
        cells.Cell(CELL_DIR / "node_visualize.py"),
    ]

    runner = GraphRunner(dag)
    await runner.run_dag_in_order()


asyncio.run(main())
