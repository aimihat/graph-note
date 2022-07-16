import re
from typing import Set
import execution.helpers.graph_helpers as graph_helpers

from proto.classes import graph_pb2

INPUT_VAR_TAG = "INPUT"
OUTPUT_VAR_TAG = "OUTPUT"


def indent_code(code: str) -> str:
    """Indents a code snippet by a tab."""

    return "\n".join(f"\t{line}" for line in code.splitlines())


def compile_cell(dag: graph_pb2.Graph, cell: graph_pb2.Cell) -> str:
    """Compiles a validated cell into code that is ready to be executed."""

    inputs = [p.name for p in cell.in_ports]
    in_port_uids = [p.uid for p in cell.in_ports]
    exec_code = cell.code

    # Replace input tags with variables.
    for ref in inputs:
        exec_code = exec_code.replace(f'{INPUT_VAR_TAG}["{ref}"]', ref)

    # Wrap cell in a function scope
    args = ", ".join(inputs)
    function = f"""def {cell.uid}({args}):\n{indent_code(exec_code)}"""

    # Call the function with the connected outputs.
    kwargs = []
    port_mapping = graph_helpers.graph_port_mapping(dag)
    for conn in dag.connections:
        if conn.target_uid in in_port_uids:
            kwargs.append(
                f"{port_mapping[conn.target_uid].name}=OUT_PORT_VALUES['{port_mapping[conn.source_uid].name}']"
            )
    function_call = f"{cell.uid}({','.join(kwargs)})"

    exec_code = f"{function}\n{function_call}"
    return exec_code


def detect_tag(code: str, tag: str) -> Set[str]:
    """Parses an input reference formatted as `Input["example_tag"]`"""
    pattern = rf"{tag}\[\"([a-zA-Z0-9_]+)\"\]"
    matches = set(re.findall(pattern, code))

    return matches
