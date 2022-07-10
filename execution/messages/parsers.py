import enum
from typing import Any, Dict, Optional
import re
from execution.messages import definitions


class HandledMessages(enum.Enum):
    stream = "stream"
    error = "error"


def parse_ansi_escape(text):
    ansi_escape = re.compile(r'''
        \x1B  # ESC
        (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
        |     # or [ for CSI, followed by a control sequence
            \[
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        )
    ''', re.VERBOSE)
    return ansi_escape.sub('', text)

def parse_message(message: Dict[str, Any]) -> definitions.Message:
    raw_message = definitions.Message(
        header=message["header"],
        msg_id=message["msg_id"],
        msg_type=message["msg_type"],
        parent_header=message["parent_header"],
        metadata=message["metadata"],
        content=message["content"],
    )

    raw_message.content = parse_content(raw_message)

    return raw_message  # no longer raw


def parse_content(message: definitions.Message) -> Optional[definitions.Content]:
    handled_messages = set(item.value for item in HandledMessages)

    if message.msg_type not in handled_messages:
        return None

    message_type = HandledMessages[message.msg_type]

    if message_type == message_type.stream:
        assert type(message.content) == dict
        if message.content["name"] == "stdout":
            return definitions.CellStdout(
                message.content["name"], message.content["text"]
            )
        elif message.content["name"] == "stderr":
            return definitions.CellStderr(
                message.content["name"], message.content["text"]
            )
    elif message_type == message_type.error:
        assert type(message.content) == dict
        return definitions.CellError(
            error=message.content["ename"],
            traceback="\n".join(message.content["traceback"]),
            error_value=message.content["evalue"],
        )
    else:
        raise Exception("This shouldn't happen")
