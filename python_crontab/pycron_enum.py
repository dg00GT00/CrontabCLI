from enum import Enum


class _EnumMixin:
    def build_args(self) -> str:
        return "--" + self.value

    def __str__(self) -> str:
        return self.value


class PyCron(_EnumMixin, Enum):
    PY = "py"
    INIT = "init"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


class SubPyCron(_EnumMixin, Enum):
    NEW = "new"
    OLD = "old"
