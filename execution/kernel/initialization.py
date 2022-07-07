"""Initialize the runtime environment to support cell outputs being recorded at global scope."""
from typing import Any, Dict, List, Union

CELL_OUTPUTS = {}


class GraphNote:
    """Encapsulates all GraphNote capabilities that are built into the runtime env."""

    @classmethod
    def out(cls, outputs: Dict[str, Any]):
        """Records the given cell output(s), taken as a dict from port names to objects."""

        if type(outputs) == dict:
            CELL_OUTPUTS.update(outputs)
        else:
            raise Exception(
                "`outputs` argument expected to be typed as Dict[str, Any]."
            )


graphnote = GraphNote()
