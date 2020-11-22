from python_crontab.icrontab_entry import ICrontabEntry
from utilities import check_args_integrity, check_pyscript_existence


class BuildPythonCrontabScript(ICrontabEntry):
    """
    Builds the formatted python script entry to insertion on cron by
    crontab command
    """

    def __init__(self):
        super(BuildPythonCrontabScript, self).__init__()
        self.py_interpreter = ""

    def set_py_interpreter(self, py_interpreter: str) -> None:
        check_pyscript_existence(py_interpreter)
        self.py_interpreter = py_interpreter

    @check_args_integrity
    def set_interval_script(self, interval: str, script: str) -> None:
        self.interval = interval
        self.script = script

    def build_cron_script(self) -> str:
        return f"*/{self.interval} * * * * {self.py_interpreter} {self.script}".strip()
