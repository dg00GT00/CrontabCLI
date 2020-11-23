from typing import NoReturn

from python_crontab.icron_entry import ICronEntry
from utilities import check_source_existence


class BuildPythonCronScript(ICronEntry):
    """
    Builds the formatted python script entry to insertion on cron by
    crontab command
    """

    def __init__(self):
        super(BuildPythonCronScript, self).__init__()
        self._py_interpreter = ""

    def set_py_interpreter(self, py_interpreter: str) -> NoReturn:
        check_source_existence(py_interpreter)
        self._py_interpreter = py_interpreter

    def build_cron_script(self) -> str:
        return f"*/{self.interval} * * * * {self._py_interpreter} {self.script}".strip()
