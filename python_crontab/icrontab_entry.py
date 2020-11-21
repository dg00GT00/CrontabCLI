import abc


class ICrontabEntry(abc.ABC):
    """
    Interface for setting a python script entry through crontab command
    """

    @abc.abstractmethod
    def set_interval_script(self, interval: str, py_script: str) -> None:
        """Sets the interval and the python script path"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_py_interpreter(self, py_interpreter: str) -> None:
        """Sets the path for python interpreter"""
        raise NotImplementedError
