from dataclasses import dataclass
import dataclasses
import inspect
import logging
import time
from typing import Any, Dict

import jupyter_client

from execution.helpers.code_helpers import compile_cell
from execution.helpers.graph_helpers import (
    ValidationResult,
    update_out_ports,
    validate_cell,
    validate_root,
    reset_out_ports,
)
from execution.messages import definitions, parsers
from execution.kernel import initialization
from proto.classes import graph_pb2


class GraphExecutorState:
    out_port_metadata: Dict[str, Any] = {}
    cell_exec_success: Dict[
        str, bool
    ] = {}  # TODO: replace once error included in dependency_status


class GraphExecutor:
    def __init__(
        self, client: jupyter_client.BlockingKernelClient, dag: graph_pb2.Graph
    ) -> None:
        self.dag = dag
        self.client = client
        self.logger = logging.getLogger()
        self.executor_state = GraphExecutorState()

    async def initialize(self):
        # TODO: this shouldn't be done here.
        self.logger.info("Initializing kernel.")
        await self.client._async_execute_interactive(inspect.getsource(initialization))

        self.logger.info("Initializing graph.")
        # Reset all output ports.
        reset_out_ports(self.dag)

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
        self.executor_state.cell_exec_success[cell.uid] = True
        cell_validation = validate_cell(self.dag, cell)

        if cell_validation == ValidationResult.CAN_BE_EXECUTED:
            exec_code = compile_cell(self.dag, cell)
            update_cell_output_ = lambda msg: self.update_cell_output(cell, msg)

            await self.client._async_execute_interactive(
                exec_code, output_hook=update_cell_output_
            )

            # Check what outputs were updated during the last cell execution.
            await self.client._async_execute_interactive(
                "print(json.dumps(OUT_PORT_METADATA))",
                output_hook=lambda msg: update_out_ports(
                    self.executor_state, cell, msg
                ),
            )

            cell.last_executed = int(time.time_ns())
            self.update_dependency_statuses(self.dag, last_cell=cell)

        elif cell_validation == ValidationResult.DISCONNECTED_INPUT:
            raise Exception("Not all cell inputs are connected.")
        elif cell_validation == ValidationResult.INPUT_MISSING_RUNTIME_VAL:
            raise Exception("Not all cell inputs have a runtime value.")
        else:
            raise Exception("Unknown cell validation error.")

    def update_cell_output(self, cell: graph_pb2.Cell, msg: Dict[str, Any]) -> None:
        # TODO: move this elsewhere
        parsed_message = parsers.parse_message(msg)

        if type(parsed_message.content) == definitions.CellStdout:
            cell.output += parsed_message.content.text
        elif type(parsed_message.content) == definitions.CellStderr:
            cell.output += parsed_message.content.text
            self.executor_state.cell_exec_success[cell.uid] = False
        elif type(parsed_message.content) == definitions.CellError:
            cell.output += f"{parsed_message.content.error}: {parsed_message.content.error_value}\n{parsed_message.content.traceback}"
            self.executor_state.cell_exec_success[cell.uid] = False
        else:
            logging.warning("Unknown output type.")

    def update_dependency_statuses(
        self, dag: graph_pb2.Graph, last_cell: graph_pb2.Cell
    ) -> None:
        """This method updates a cell's dependency status.

        The status can be either:
        - NOT_EXECUTED
        - INPUT_PORT_OUTDATED -> at least one of the cell's ancestors was executed after the cell
        - UP_TO_DATE -> all of the cell's ancestors were executed earlier than the cell

        Note: after a cell is executed, we only need to update that cell and its descendents.
        """

        # TODO: separate UP_TO_DATE into success/failure states?
        def outdate_descendents(cell: graph_pb2.Cell) -> None:
            out_uids = [p.uid for p in cell.out_ports]
            descendant_ports = set(
                c.target_uid for c in dag.connections if c.source_uid in out_uids
            )
            descendant_cells = [
                c
                for c in dag.cells
                if descendant_ports.intersection(p_.uid for p_ in c.in_ports)
            ]
            for c in descendant_cells:
                if c.dependency_status == graph_pb2.Cell.UP_TO_DATE:
                    c.dependency_status = graph_pb2.Cell.INPUT_PORT_OUTDATED
                    outdate_descendents(c)
                elif c.dependency_status in [
                    graph_pb2.Cell.NOT_EXECUTED,
                    graph_pb2.Cell.INPUT_PORT_OUTDATED,
                ]:
                    pass
                else:
                    raise Exception(
                        f"Unhandled dependency status {c.dependency_status}"
                    )

        def ancestors_up_to_date(cell: graph_pb2.Cell) -> bool:
            in_uids = [p.uid for p in cell.in_ports]
            ancestor_ports = set(
                [c.source_uid for c in dag.connections if c.target_uid in in_uids]
            )
            ancestor_cells = [
                c
                for c in dag.cells
                if ancestor_ports.intersection(p_.uid for p_ in c.out_ports)
            ]

            if not ancestor_cells:
                return True

            if any(
                c.dependency_status != graph_pb2.Cell.UP_TO_DATE for c in ancestor_cells
            ):
                return False

            return all(ancestors_up_to_date(c) for c in ancestor_cells)

        if last_cell.dependency_status == graph_pb2.Cell.NOT_EXECUTED:
            # None of the descendents could have been previously executed.
            # Therefore, we only need to update the cell itself.
            if ancestors_up_to_date(last_cell):
                last_cell.dependency_status = graph_pb2.Cell.UP_TO_DATE
            else:
                last_cell.dependency_status = graph_pb2.Cell.INPUT_PORT_OUTDATED
        elif last_cell.dependency_status == graph_pb2.Cell.INPUT_PORT_OUTDATED:
            # If the cell was outdated, that means its descents are also outdated.
            # Therefore, we only need to update the cell itself.
            if ancestors_up_to_date(last_cell):
                last_cell.dependency_status = graph_pb2.Cell.UP_TO_DATE
        elif last_cell.dependency_status == graph_pb2.Cell.UP_TO_DATE:
            # We update all descendents to be out-of-date, or not-executed.
            outdate_descendents(last_cell)
        else:
            raise Exception(
                f"Unhandled dependency status {last_cell.dependency_status}"
            )

        # TODO: move this elsewhere
