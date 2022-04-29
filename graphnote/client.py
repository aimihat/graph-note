import asyncio
import dataclasses
from pathlib import Path
from typing import Any

import jupyter_client

import message_parser
import messages
from dags import Node

CELL_DIR = Path(__file__).parent.parent / "cells"
KERNEL_SPEC_DIR = Path("/Users/aimilioshatzistamou/Library/Jupyter/runtime/")

client = jupyter_client.BlockingKernelClient()

# Get connection info
client.load_connection_file(str(KERNEL_SPEC_DIR / "kernel-72378.json"))
client.start_channels()


class GraphRunner:
    def __init__(self, dag):
        self.dag = dag
        self.parser = message_parser.MessageParser()

    def display_execution_output(self, msg: Any) -> None:
        parsed_message = self.parser.parse_message(msg)
        if type(parsed_message.content) == messages.CellStdout:
            print(parsed_message.content.text)

    async def run_node(self, node):
        await client._async_execute_interactive(
            node.code, output_hook=self.display_execution_output
        )

    async def run_dag_in_order(self):
        for node in self.dag:
            print(
                f"Executing {node.filepath}, with inputs {node.input_vars}, and outputs {node.output_vars}"
            )
            await self.run_node(node)


async def main():
    dag = [
        Node(CELL_DIR / "node_root.py"),
        Node(CELL_DIR / "node_data.py"),
        Node(CELL_DIR / "node_trainer.py"),
        Node(CELL_DIR / "node_visualize.py"),
    ]

    runner = GraphRunner(dag)
    await runner.run_dag_in_order()


asyncio.run(main())
