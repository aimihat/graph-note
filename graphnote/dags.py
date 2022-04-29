from typing import List

INPUT_VAR_TAG = "inputvar"
OUTPUT_VAR_TAG = "inputvar"


class Node:
    def __init__(self, filepath: str) -> None:
        with open(filepath, "r") as f:
            self.code = f.read()

        self.input_vars = self.parse_tag(INPUT_VAR_TAG)
        self.output_vars = self.parse_tag(OUTPUT_VAR_TAG)

    def parse_tag(self, tag: str) -> List[str]:
        """Parses a tag line, formatted as `# tag: TAG_TO_EXTRACT`"""
        lines = self.code.split("\n")

        tag_lines = [line for line in lines if tag in line]
        tags = [line.split(" ")[-1].strip() for line in tag_lines]

        self.code = "\n".join([line for line in lines if tag not in line])
        return tags
