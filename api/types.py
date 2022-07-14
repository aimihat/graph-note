import enum
from pydantic import BaseModel


class APIResponses(enum.Enum):
    UpdatedGraph = 200
    ErrorMessage = 206


class RequestBodyGraph(BaseModel):
    b64_graph: str
