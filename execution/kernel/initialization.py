"""Initialize the runtime environment to support cell outputs being recorded at global scope."""
from typing import Any, Dict
import time

OUT_PORT_VALUES = {}
OUT_PORT_METADATA = {}


class GraphNote:
    """Encapsulates all GraphNote capabilities that are built into the runtime env."""

    @classmethod
    def out(cls, outputs: Dict[str, Any]):
        """Records the given cell output(s), taken as a dict from port names to objects."""

        if type(outputs) == dict:
            OUT_PORT_VALUES.update(outputs)
            OUT_PORT_METADATA.update({k: int(time.time()) for k in outputs.keys()})
        else:
            raise Exception(
                "`outputs` argument expected to be typed as Dict[str, Any]."
            )


graphnote = GraphNote()
