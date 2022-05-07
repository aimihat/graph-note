import inspect
from typing import Any

import jupyter_client

from graphnote.dag.cells import Cell, Root
from graphnote.dag.graph import Dagbook
from graphnote.kernel import initialization
from graphnote.message import defs, parser


class GraphRunner:
    def __init__(
        self, client: jupyter_client.BlockingKernelClient, dag: Dagbook
    ) -> None:
        self.dag = dag
        self.client = client
        self.parser = parser.MessageParser()

    async def init_kernel(self):
        # TODO: this shouldn't be done here.
        await self.client._async_execute_interactive(inspect.getsource(initialization))

    def display_execution_output(self, msg: Any) -> None:
        parsed_message = self.parser.parse_message(msg)
        if type(parsed_message.content) == defs.CellStdout:
            print(parsed_message.content.text)
        elif type(parsed_message.content) == defs.CellStderr:
            print(parsed_message.content.text)

    async def run_root(self, root: Root) -> None:
        if self.dag.root_is_valid(root):
            print(f"Executing root node.")
            reply = await self.client._async_execute_interactive(
                root.code, output_hook=self.display_execution_output
            )
            if reply["content"]["status"] == "error":
                traceback = reply["content"]["traceback"]
                for trace in traceback:
                    print(trace)
        else:
            raise Exception("The root is not valid and cannot be run.")

    async def run_cell(self, cell: Cell) -> None:
        # Ensure the cell is compiled & can be run
        cell.compile()
        print(
            f"Executing {cell.uid}, with inputs {cell.input_vars}, and outputs {cell.output_vars}"
        )
        if self.dag.cell_is_valid(cell):
            reply = await self.client._async_execute_interactive(
                cell.compiled_code, output_hook=self.display_execution_output
            )
            if reply["content"]["status"] == "error":
                traceback = reply["content"]["traceback"]
                for trace in traceback:
                    print(trace)
            print("Cell finished executing.")
        else:
            raise Exception("The cell is not valid and cannot be run.")

    async def run_dag_in_order(self):
        # TODO: before starting to run indiv. cells, confirm the entire DAG is valid.
        # Run cells by order of dependency.
        await self.run_root(self.dag.root)
        self.dag.compile()
        for cell in self.dag.iter():
            await self.run_cell(cell)
