import inspect
import logging
from typing import Any

import jupyter_client

from graphnote.execution.cells import Cell, Root
from graphnote.execution.code_helpers import compile_cell
from graphnote.execution.graph_helpers import (Dagbook, validate_cell,
                                               validate_root)
from graphnote.kernel import initialization
from graphnote.message import defs, parser


class GraphExecutor:
    def __init__(
        self, client: jupyter_client.BlockingKernelClient, dag: Dagbook
    ) -> None:
        self.dag = dag
        self.client = client
        self.logger = logging.getLogger()

    async def init_kernel(self):
        # TODO: this shouldn't be done here.
        await self.client._async_execute_interactive(inspect.getsource(initialization))

    async def run_root(self, root: Root) -> None:
        if validate_root(root):
            self.logger.info(f"Executing root node.")
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
        self.logger.info(
            f"Executing {cell.uid}, with inputs {cell.in_ports}, and outputs {cell.out_ports}"
        )
        if validate_cell(cell):
            exec_code = compile_cell(cell)
            reply = await self.client._async_execute_interactive(
                exec_code, output_hook=self.display_execution_output
            )
            # TODO: convert this to use message interface.
            if reply["content"]["status"] == "error":
                traceback = reply["content"]["traceback"]
                for trace in traceback:
                    print(trace)
        else:
            raise Exception("The cell is not valid and cannot be run.")

    def display_execution_output(self, msg: Any) -> None:
        parsed_message = self.parser.parse_message(msg)
        if type(parsed_message.content) == defs.CellStdout:
            print(parsed_message.content.text)
        elif type(parsed_message.content) == defs.CellStderr:
            print(parsed_message.content.text)
