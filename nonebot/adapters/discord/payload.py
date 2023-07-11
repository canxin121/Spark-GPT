from enum import IntEnum
from typing_extensions import Literal, Annotated
from typing import TYPE_CHECKING, Any, Union, Optional

from pydantic import Extra, Field, BaseModel

from .api.model import Hello as HelloData
from .utils import json_dumps, json_loads
from .api.model import Resume as ResumeData
from .api.model import Identify as IdentifyData

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny, MappingIntStrAny, AbstractSetIntStr


class Opcode(IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    RESUME = 6
    RECONNECT = 7
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class Payload(BaseModel):
    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True
        json_loads = json_loads
        json_dumps = json_dumps

    def dict(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny", None] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny", None] = None,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        **kwargs: Any,
    ) -> "DictStrAny":
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=True,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )


class Dispatch(Payload):
    opcode: Literal[Opcode.DISPATCH] = Field(Opcode.DISPATCH, alias="op")
    data: dict = Field(alias="d")
    sequence: int = Field(alias="s")
    type: str = Field(alias="t")


class Heartbeat(Payload):
    opcode: Literal[Opcode.HEARTBEAT] = Field(Opcode.HEARTBEAT, alias="op")
    data: Optional[int] = Field(alias="d")


class Identify(Payload):
    opcode: Literal[Opcode.IDENTIFY] = Field(Opcode.IDENTIFY, alias="op")
    data: IdentifyData = Field(alias="d")


class Resume(Payload):
    opcode: Literal[Opcode.RESUME] = Field(Opcode.RESUME, alias="op")
    data: ResumeData = Field(alias="d")


class Reconnect(Payload):
    opcode: Literal[Opcode.RECONNECT] = Field(Opcode.RECONNECT, alias="op")


class InvalidSession(Payload):
    opcode: Literal[Opcode.INVALID_SESSION] = Field(Opcode.INVALID_SESSION, alias="op")


class Hello(Payload):
    opcode: Literal[Opcode.HELLO] = Field(Opcode.HELLO, alias="op")
    data: HelloData = Field(alias="d")


class HeartbeatAck(Payload):
    opcode: Literal[Opcode.HEARTBEAT_ACK] = Field(Opcode.HEARTBEAT_ACK, alias="op")


PayloadType = Union[
    Annotated[
        Union[Dispatch, Reconnect, InvalidSession, Hello, HeartbeatAck],
        Field(discriminator="opcode"),
    ],
    Payload,
]
