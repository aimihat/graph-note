import dataclasses
from typing import Any, Dict, Union

### Types: Message Content ###


@dataclasses.dataclass
class CellStdout:
    name: str
    text: str


@dataclasses.dataclass
class CellStderr:
    name: str
    text: str


RawContent = Dict[str, Any]

Content = Union[RawContent, CellStdout, CellStderr]


@dataclasses.dataclass
class Message:
    header: Dict
    msg_id: str
    msg_type: str
    parent_header: Dict
    metadata: Dict
    content: Content
