from typing_extensions import TypeAlias
from typing import Any, Dict, Union, Literal, TypeVar, final, Optional

T = TypeVar("T")


@final
class MissingType:
    """MissingType is a singleton class of MISSING.

    MISSING means that the field maybe not given in the data.

    MISSING Not equivalent to Python's Optional.

    see https://discord.com/developers/docs/reference#nullable-and-optional-resource-fields
    """

    _instance: Optional["MissingType"] = None

    def __new__(cls) -> "MissingType":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<MISSING>"

    def __str__(self) -> str:
        return self.__repr__()

    def __bool__(self) -> Literal[False]:
        return False

    def __copy__(self):
        return MISSING

    def __deepcopy__(self, memo: Dict[int, Any]):
        return MISSING

    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @classmethod
    def _validate(cls, value: Any):
        if value is not MISSING:
            raise ValueError(f"{value!r} is not MISSING type")
        return value


MISSING = MissingType()
"""MISSING means that the field maybe not given in the data.

see https://discord.com/developers/docs/reference#nullable-and-optional-resource-fields"""

Missing: TypeAlias = Union[MissingType, T]
"""Missing means that the field maybe not given in the data.

Missing[T] equal to Union[MISSING, T].

example: Missing[int] == Union[MISSING, int]"""

MissingOrNullable: TypeAlias = Union[MissingType, T, None]
"""MissingOrNullable means that the field maybe not given in the data or value is None.

MissingOrNullable[T] equal to Union[MISSING, T, None].

example: MissingOrNullable[int] == Union[MISSING, int, None]"""

__all__ = ["MISSING", "Missing", "MissingOrNullable"]
