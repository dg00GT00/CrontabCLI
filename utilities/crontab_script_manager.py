import io
import re
from typing import TypeVar

from python_crontab.icrontab_entry import ICrontabEntry
from utilities import run_bash_cmd, regex_builder

Self = TypeVar("Self", bound="CrontabScriptManager")


class CrontabScriptManager:
    """
    Manages the "CRUD" operation done in the cron scripts
    """

    def __init__(self, crontab_gen: ICrontabEntry):
        self.crontab_gen = crontab_gen
        self.was_entry_modified = False
        self._base_crontab_command = run_bash_cmd(["crontab", "-l"], show_output=True)
        self._cron_io: io.TextIOWrapper = self._base_crontab_command.result
        self.some_entry_exists: bool = True if self._base_crontab_command.return_code == 0 else False

    def clear_crontab_entries(self) -> None:
        run_bash_cmd(["crontab", "-r"])

    def insert_new_crontab(self) -> str:
        new_cron_script = self.crontab_gen.build_cron_script()
        cron_io = io.StringIO()
        while True:
            line = self._cron_io.readline()
            if line:
                if new_cron_script in line:
                    self.was_entry_modified = True
                    break
                cron_io.write(line)
            else:
                break
        cron_io.write(new_cron_script)
        update_crontab_script = cron_io.getvalue()
        cron_io.close()
        self.clear_crontab_entries()
        return update_crontab_script.strip()

    def remove_crontab_entry(self) -> str:
        cron_io = io.StringIO()
        cron_script = self.crontab_gen.build_cron_script()
        while True:
            line = self._cron_io.readline()
            if line:
                if cron_script in line:
                    line = ""
                    self.was_entry_modified = True
                cron_io.write(line)
            else:
                break
        update_crontab_script = cron_io.getvalue()
        cron_io.close()
        self.clear_crontab_entries()
        return update_crontab_script.strip()

    def update_crontab(self, keep_part: str) -> str:
        cron_script = self._cron_io.read().strip()
        new_script = re.sub(regex_builder(keep_part, self.crontab_gen.script),
                            self.crontab_gen.interval,
                            cron_script, count=1)
        self.clear_crontab_entries()
        return new_script.strip()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._cron_io.close()
        return False
