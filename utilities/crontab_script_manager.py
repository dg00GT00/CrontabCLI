import io
import re
from typing import TypeVar

from python_crontab.icrontab_entry import ICrontabEntry
from utilities import run_bash_cmd

Self = TypeVar("Self", bound="CrontabScriptManager")


class CrontabScriptManager:
    """
    Manages the "CRUD" operation done in the cron scripts
    """

    def __init__(self, crontab_gen: ICrontabEntry):
        self.crontab_gen = crontab_gen
        self._base_crontab_command = run_bash_cmd(["crontab", "-l"], show_output=True)
        self._cron_io: io.TextIOWrapper = self._base_crontab_command.result
        self.some_entry_exists: bool = True if self._base_crontab_command.return_code == 0 else False

    def clear_crontab_entries(self) -> None:
        run_bash_cmd(["crontab", "-r"])

    def get_current_crontab(self) -> str:
        return self._cron_io.read().strip()

    def insert_new_crontab(self) -> str:
        current_cron_script = self.get_current_crontab()
        new_cron_script = self.crontab_gen.build_cron_script()
        cron_io = io.StringIO()
        cron_io.write(current_cron_script + '\n')
        cron_io.write(new_cron_script)
        update_crontab_script = cron_io.getvalue()
        cron_io.close()
        self.clear_crontab_entries()
        return update_crontab_script.strip()

    def update_crontab(self, keep_part: str) -> str:
        escape = re.escape(self.crontab_gen.script)
        cron_script = self.get_current_crontab()
        new_script = re.sub(fr"(?<=\*/)\d+(?=(?:\s\*)+\s+{keep_part}\d*\.*\d*\s*{escape})",
                            self.crontab_gen.interval,
                            cron_script, count=1)
        self.clear_crontab_entries()
        return new_script.strip()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._cron_io.close()
        return False
