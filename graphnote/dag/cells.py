import dataclasses
import pathlib
import re
from typing import List, Optional, Set, Tuple

INPUT_VAR_TAG = "INPUT"
OUTPUT_VAR_TAG = "OUTPUT"


class CodeHandler:
    """Helper class for parsing and transforming cell code."""

    def indent_code(self, code: str) -> str:
        """Indents a code snippet by a tab"""
        return "\n".join(f"\t{line}" for line in code.splitlines())

    def parse_tag(self, code: str, tag: str) -> Tuple[Set[str], str]:
        """Parses an input reference formatted as `Input["example_tag"]`"""
        pattern = rf"{tag}\[\"([a-zA-Z0-9_]+)\"\]"
        matches = set(re.findall(pattern, code))

        for ref in matches:
            code = code.replace(f'{tag}["{ref}"]', ref)

        return matches, code


@dataclasses.dataclass
class Cell:
    filepath: str
    id: str
    input_vars: Optional[set]
    output_vars: Optional[set]
    compiled_code: Optional[str]

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.id = pathlib.Path(filepath).stem
        self.code_handler = CodeHandler()

    def load_code(self) -> str:
        with open(self.filepath, "r") as f:
            return f.read()

    def compile(self):
        raw_code = self.load_code()

        # Detect required inputs
        self.input_vars, raw_code = self.code_handler.parse_tag(raw_code, INPUT_VAR_TAG)
        self.output_vars = set()  # TODO

        # Wrap cell in a function scope
        func_args = ", ".join(self.input_vars)
        func_header = f"def {self.id}({func_args}):"
        indented_code = self.code_handler.indent_code(raw_code)

        self.compiled_code = f"{func_header}\n{indented_code}"

        # TODO: no dag yet
        self.compiled_code = self.compiled_code + f"\n{self.id}({func_args})"
