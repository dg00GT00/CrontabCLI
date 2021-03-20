import threading
from abc import abstractmethod
from typing import NoReturn, Optional, List, overload

from utilities import time_constraints, check_source_existence, check_pkg_existence


class ICronEntry:

    def __init__(self):
        """
        Interface for setting a generic script entry through crontab command
        @warning This interface must not implement the ABC helper class for declaring interfaces.
        This restriction is important due features of metaclass that compound the inheritance chain
        """
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

    def __init__(self):
        """
        Interface for setting a python script entry through crontab command
        """
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


class IPyCronManager:
    def __init__(self, pycron_builder: IPyCronEntry):
        """
        Manages the insertion and updating of the python script into cron
        @warning This interface must not implement the ABC helper class due to quirks
        related metaclass used in the concrete implementation of this interface
        """
        check_pkg_existence()
        super(IPyCronManager, self).__init__()
        self.successfully_command = False
        self.pycron_builder = pycron_builder
        self._script: Optional[str, List[str]] = None
        self._interval: Optional[str] = None
        self.event = threading.Event()

    @property
    def interval(self) -> str:
        return self._interval

    @interval.setter
    def interval(self, value: str) -> None:
        self._interval = value

    @property
    def script(self) -> str:
        return self._script

    @overload
    def set_script(self, script: str) -> None:
        raise NotImplementedError

    @overload
    def set_script(self, script: List[str]) -> None:
        raise NotImplementedError

    def set_script(self, script) -> None:
        self._script = script

    @abstractmethod
    def init_cron(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_cron(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def insert_new_cron(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_cron_entry(self) -> None:
        raise NotImplementedError
