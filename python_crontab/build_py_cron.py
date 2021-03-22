from typing import NoReturn

from python_crontab.interfaces.icron_entry import IPyCronEntry
from utilities import check_source_existence


class BuildPyCronScript(IPyCronEntry):
    """
    Builds the formatted python script entry to insertion on cron by
    crontab command
    """

    def __init__(self):
        super(BuildPyCronScript, self).__init__()

    def set_py_interpreter(self, py_interpreter: str) -> NoReturn:
        check_source_existence(py_interpreter)
        super().set_py_interpreter(py_interpreter)

    def build_cron_script(self) -> str:
        return f"*/{self.interval} * * * * export DISPLAY=':0'; {self.py_interpreter} {self.script} >/dev/null 2>&1".strip()


class BuildPyModuleCronScript(BuildPyCronScript):
    def build_cron_script(self) -> str:
        return f"*/{self.interval} * * * * export DISPLAY=':0'; {self.script} >/dev/null 2>&1".strip()
