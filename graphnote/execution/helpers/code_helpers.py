import re
from typing import Set

from graphnote.execution.graph_helpers import INPUT_VAR_TAG


def indent_code(self, code: str) -> str:
    """Indents a code snippet by a tab."""

    return "\n".join(f"\t{line}" for line in code.splitlines())


def compile_cell(dag, cell):
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
    for conn in dag.connections:
        if conn.to_port.uid in in_port_uids:
            kwargs.append(f"{conn.to_port.name}=CELL_OUTPUTS['{conn.from_port.name}']")
    function_call = f"cell.uid({','.join(kwargs)})"

    exec_code = f"{function}\n{function_call}"
    return exec_code


def detect_tag(code: str, tag: str) -> Set[str]:
    """Parses an input reference formatted as `Input["example_tag"]`"""
    pattern = rf"{tag}\[\"([a-zA-Z0-9_]+)\"\]"
    matches = set(re.findall(pattern, code))

    return matches
