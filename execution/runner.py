import inspect
import logging
from typing import Any

import jupyter_client

from execution.helpers.code_helpers import compile_cell
from execution.helpers.graph_helpers import validate_cell, validate_root
from execution.messages import definitions, parsers
from execution.kernel import initialization
from proto.classes import graph_pb2


class GraphExecutor:
    def __init__(
        self, client: jupyter_client.BlockingKernelClient, dag: graph_pb2.Graph
    ) -> None:
        self.dag = dag
        self.client = client
        self.logger = logging.getLogger()

    async def init_kernel(self):
        # TODO: this shouldn't be done here.
        self.logger.info("Initializing kernel.")
        await self.client._async_execute_interactive(inspect.getsource(initialization))

    async def run_root(self, root: graph_pb2.Cell) -> None:
        logging.info("Executing root node.")
        if validate_root(root):
            self.logger.info(f"Executing root node.")
            reply = await self.client._async_execute_interactive(
                root.code  # , output_hook=self.display_execution_output
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
        
        # Reset the cell output, before updating it with incoming messages.
        cell.output = ""

        if validate_cell(self.dag, cell):
            exec_code = compile_cell(self.dag, cell)
            print(exec_code, cell.code)

            update_cell_output_ = lambda msg: self.update_cell_output(cell, msg)

            await self.client._async_execute_interactive(
                exec_code, output_hook=update_cell_output_
            )
        else:
            raise Exception("Some of the cell's ins are unavailable.")

    def update_cell_output(self, cell, msg):
        # TODO: are there cases where a single execution produces both stderr and stdout?
        parsed_message = parsers.parse_message(msg)

        if type(parsed_message.content) == definitions.CellStdout:
            cell.output = parsed_message.content.text
        elif type(parsed_message.content) == definitions.CellStderr:
            cell.output = parsed_message.content.text
        elif type(parsed_message.content) == definitions.CellError:
            cell.output = f"{parsed_message.content.error}: {parsed_message.content.error_value}\n{parsed_message.content.traceback}"
        else:
            logging.warning("Unknown output type.")
