import inspect
import logging
from typing import Any

import jupyter_client

from graphnote.execution.helpers.code_helpers import compile_cell
from graphnote.execution.helpers.graph_helpers import (validate_cell,
                                                       validate_root)
from graphnote.execution.messages import definitions, parsers
from graphnote.kernel import initialization
from graphnote.proto.classes import graph_pb2


class GraphExecutor:
    def __init__(
        self, client: jupyter_client.BlockingKernelClient, dag: graph_pb2.Graph
    ) -> None:
        self.dag = dag
        self.client = client
        self.logger = logging.getLogger()

    async def init_kernel(self):
        # TODO: this shouldn't be done here.
        await self.client._async_execute_interactive(inspect.getsource(initialization))

    async def run_root(self, root: graph_pb2.Cell) -> None:
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

    async def run_cell(self, cell: graph_pb2.Cell) -> None:
        self.logger.info(
            f"Executing {cell.uid}, with inputs {cell.in_ports}, and outputs {cell.out_ports}"
        )
        if validate_cell(self.dag, cell):
            exec_code = compile_cell(self.dag, cell)
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
        parsed_message = parsers.parse_message(msg)
        if type(parsed_message.content) == definitions.CellStdout:
            print(parsed_message.content.text)
        elif type(parsed_message.content) == definitions.CellStderr:
            print(parsed_message.content.text)
