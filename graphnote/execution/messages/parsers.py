import enum
from typing import Any

from graphnote.message import defs


class HandledMessages(enum.Enum):
    stream = "stream"


def parse_message(message: Any) -> defs.Message:
    raw_message = defs.Message(
        header=message["header"],
        msg_id=message["msg_id"],
        msg_type=message["msg_type"],
        parent_header=message["parent_header"],
        metadata=message["metadata"],
        content=message["content"],
    )

    raw_message.content = parse_content(raw_message)

    return raw_message  # no longer raw


def parse_content(message: defs.Message):
    handled_messages = set(item.value for item in HandledMessages)

    if message.msg_type not in handled_messages:
        return None

    message_type = HandledMessages[message.msg_type]

    if message_type == message_type.stream:
        assert type(message.content) == dict
        if message.content["name"] == "stdout":
            return defs.CellStdout(message.content["name"], message.content["text"])
        elif message.content["name"] == "stderr":
            return defs.CellStderr(message.content["name"], message.content["text"])
