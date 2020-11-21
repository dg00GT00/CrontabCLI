import abc


class ICrontabEntry(abc.ABC):
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
    def interval(self, value: str):
        self._interval = value

    @property
    def script(self) -> str:
        return self._script

    @script.setter
    def script(self, value: str):
        self._script = value

    @abc.abstractmethod
    def set_interval_script(self, interval: str, script: str) -> None:
        """Sets the interval and the python script path"""
        raise NotImplementedError

    @abc.abstractmethod
    def build_cron_script(self) -> str:
        """Builds the properly formatted crontab script"""
        raise NotImplementedError
