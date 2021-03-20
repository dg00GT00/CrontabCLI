from abc import abstractmethod, ABC
from typing import NoReturn, Optional

from utilities import time_constraints, check_source_existence


class ICronEntry(ABC):
    """
    Interface for setting a generic script entry through crontab command
    """

    def __init__(self):
        self._script = ""
        self._interval = ""

    @property
    def interval(self) -> str:
        return self._interval

    @interval.setter
    def interval(self, value: str) -> NoReturn:
        time_constraints(value)
        self._interval = value

    @property
    def script(self) -> str:
        return self._script

    @script.setter
    def script(self, value: str) -> NoReturn:
        check_source_existence(value)
        self._script = value

    @abstractmethod
    def build_cron_script(self) -> str:
        """Builds the properly formatted crontab script"""
        raise NotImplementedError


class IPyCronEntry(ICronEntry):
    """
    Interface for setting a python script entry through crontab command
    """

    def __init__(self):
        super(IPyCronEntry, self).__init__()
        self._py_interpreter: Optional[str] = None

    @property
    def py_interpreter(self) -> str:
        return self._py_interpreter

    @abstractmethod
    def set_py_interpreter(self, py_interpreter: str) -> NoReturn:
        """
        Sets the python interpreter for building the cron script entry
        @param py_interpreter: the python interpreter
        """
        self._py_interpreter = py_interpreter
