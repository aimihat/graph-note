from pathlib import Path
from typing import Any

import jupyter_client

from graphnote.message import defs, parser

KERNEL_SPEC_DIR = Path("/Users/aimilioshatzistamou/Library/Jupyter/runtime/")

client = jupyter_client.BlockingKernelClient()
client.load_connection_file(str(KERNEL_SPEC_DIR / "kernel-72378.json"))
client.start_channels()


class GraphRunner:
    def __init__(self, dag):
        self.dag = dag
        self.parser = parser.MessageParser()

    def display_execution_output(self, msg: Any) -> None:
        parsed_message = self.parser.parse_message(msg)
        if type(parsed_message.content) == defs.CellStdout:
            print(parsed_message.content.text)
        elif type(parsed_message.content) == defs.CellStderr:
            print(parsed_message.content.text)

    async def run_node(self, node):
        node.compile()

        print(
            f"Executing {node.id}, with inputs {node.input_vars}, and outputs {node.output_vars}"
        )

        reply = await client._async_execute_interactive(
            node.compiled_code, output_hook=self.display_execution_output
        )
        if reply["content"]["status"] == "error":
            traceback = reply["content"]["traceback"]
            for trace in traceback:
                print(trace)

    async def run_dag_in_order(self):
        for node in self.dag:
            await self.run_node(node)
