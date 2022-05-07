import dataclasses
import pathlib
import re
from typing import List, Optional, Set, Tuple

from graphnote.dag.code_manager import CodeHandler

INPUT_VAR_TAG = "INPUT"
OUTPUT_VAR_TAG = "OUTPUT"


CellUID = str


@dataclasses.dataclass
class Port:
    cell_uid: CellUID
    name: str


@dataclasses.dataclass
class Connection:
    from_port: Port
    to_port: Port


@dataclasses.dataclass
class Cell:
    filepath: str
    uid: CellUID
    input_vars: Optional[set]
    output_vars: Optional[set]
    compiled_code: Optional[str]

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.uid = pathlib.Path(filepath).stem
        self.code_handler = CodeHandler()

    def load_code(self) -> str:
        with open(self.filepath, "r") as f:
            return f.read()

    def compile(self):  # TODO: move this to be called in the runner
        raw_code = self.load_code()

        # Detect required inputs
        self.input_vars, raw_code = self.code_handler.parse_tag(raw_code, INPUT_VAR_TAG)
        self.output_vars = set()  # TODO

        # Wrap cell in a function scope
        func_args = ", ".join(self.input_vars)
        func_header = f"def {self.uid}({func_args}):"
        indented_code = self.code_handler.indent_code(raw_code)

        self.compiled_code = f"{func_header}\n{indented_code}"

        in_from_recorded_outs = [f"CELL_OUTPUTS['{in_}']" for in_ in self.input_vars]
        call_args = ",".join(in_from_recorded_outs)
        self.compiled_code = self.compiled_code + f"\n{self.uid}({call_args})"


@dataclasses.dataclass
class Root:
    filepath: str
    code: str

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.code = self.load_code()

    def load_code(self) -> str:
        with open(self.filepath, "r") as f:
            return f.read()
