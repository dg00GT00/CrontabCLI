import abc
from typing import NoReturn

from utilities import time_constraints, check_source_existence


class ICronEntry(abc.ABC):
    """
    Interface for setting a python script entry through crontab command
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

    @abc.abstractmethod
    def build_cron_script(self) -> str:
        """Builds the properly formatted crontab script"""
        raise NotImplementedError
