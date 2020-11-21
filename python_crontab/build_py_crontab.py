from typing import Tuple

from python_crontab.icrontab_entry import ICrontabEntry
from utilities import check_args_integrity, check_pyscript_existence


class BuildPythonCrontabScript(ICrontabEntry):
    """
    Builds the formatted python script entry to insertion on cron by
    crontab command
    """

    def __init__(self):
        self.py_interpreter = ""
        self.interval_script: Tuple[str, str] = ("", "")

    def set_py_interpreter(self, py_interpreter: str) -> None:
        check_pyscript_existence(py_interpreter)
        self.py_interpreter = py_interpreter

    @check_args_integrity
    def set_interval_script(self, interval: str, py_script: str) -> None:
        self.interval_script = (interval, py_script)

    def build_script(self) -> str:
        interval, py_script = self.interval_script
        return f"*/{interval} * * * * {self.py_interpreter} {py_script}"
