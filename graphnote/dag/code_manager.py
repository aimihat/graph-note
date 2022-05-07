import re
from typing import List, Set, Tuple


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
