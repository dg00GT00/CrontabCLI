import io
from typing import TypeVar

from python_crontab.icron_entry import ICronEntry
from utilities import run_bash_cmd

Self = TypeVar("Self", bound="CronScriptManager")


class CronScriptManager:
    """
    Manages the "CRUD" operation done in the cron scripts
    """

    def __init__(self, crontab_gen: ICronEntry):
        self.crontab_gen = crontab_gen
        self.was_entry_modified = False
        self._base_crontab_command = run_bash_cmd(["crontab", "-l"], show_output=True)
        self._cron_io: io.TextIOWrapper = self._base_crontab_command.result
        self.some_entry_exists: bool = True if self._base_crontab_command.return_code == 0 else False

    def clear_cron_entries(self) -> None:
        run_bash_cmd(["crontab", "-r"])

    def insert_new_cron(self) -> str:
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
        self.clear_cron_entries()
        return update_crontab_script.strip()

    def remove_cron_entry(self) -> str:
        cron_script = self.crontab_gen.build_cron_script()
        cron_io = io.StringIO()
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
        self.clear_cron_entries()
        return update_crontab_script.strip()

    def update_cron(self, old_cron_entry: str, new_cron_entry: str) -> str:
        cron_io = io.StringIO()
        while True:
            line = self._cron_io.readline()
            if line:
                if old_cron_entry in line:
                    line = new_cron_entry + "\n"
                    self.was_entry_modified = True
                cron_io.write(line)
            else:
                break
        update_crontab_script = cron_io.getvalue()
        cron_io.close()
        self.clear_cron_entries()
        return update_crontab_script.strip()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._cron_io.close()
        return False
