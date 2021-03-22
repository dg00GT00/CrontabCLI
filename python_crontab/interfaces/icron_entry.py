import threading
from abc import abstractmethod, ABC
from typing import NoReturn, Optional

from utilities import time_constraints, check_pkg_existence


class ICronEntry(ABC):

    def __init__(self):
        """
        Interface for setting a generic script entry through crontab command
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
    def script(self, value: str) -> None:
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
        self.event = threading.Event()

    @property
    def interval(self) -> str:
        return self.pycron_builder.interval

    @interval.setter
    def interval(self, value: str) -> None:
        self.pycron_builder.interval = value

    @property
    def script(self) -> str:
        return self.pycron_builder.script

    def set_script(self, script: str) -> None:
        self.pycron_builder.script = script

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
