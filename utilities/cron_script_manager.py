import io
from typing import TypeVar, Callable

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
        self._new_cron_io = io.StringIO()
        self._base_crontab_command = run_bash_cmd(["crontab", "-l"], show_output=True)
        self._cron_io: io.TextIOWrapper = self._base_crontab_command.result
        self.some_entry_exists: bool = True if self._base_crontab_command.return_code == 0 else False

    def _io_wrapper(self, func: Callable[..., str]) -> Callable[..., str]:
        def inner(*args, **kwargs) -> str:
            update_crontab_script = func(*args, **kwargs)
            self._new_cron_io.close()
            self.clear_cron_entries()
            return update_crontab_script.strip()

        return inner

    def __getattr__(self, item) -> Callable[..., str]:
        if callable(item):
            return self._io_wrapper(item)

    def clear_cron_entries(self) -> None:
        run_bash_cmd(["crontab", "-r"])

    def insert_new_cron(self) -> str:
        new_cron_script = self.crontab_gen.build_cron_script()
        while True:
            line = self._cron_io.readline()
            if line:
                if new_cron_script in line:
                    self.was_entry_modified = True
                    break
                self._new_cron_io.write(line)
            else:
                break
        self._new_cron_io.write(new_cron_script)
        return self._new_cron_io.getvalue()

    def remove_cron_entry(self) -> str:
        cron_script = self.crontab_gen.build_cron_script()
        while True:
            line = self._cron_io.readline()
            if line:
                if cron_script in line:
                    line = ""
                    self.was_entry_modified = True
                self._new_cron_io.write(line)
            else:
                break
        return self._new_cron_io.getvalue()

    def update_cron(self, old_cron_entry: str, new_cron_entry: str) -> str:
        while True:
            line = self._cron_io.readline()
            if line:
                if old_cron_entry in line:
                    line = new_cron_entry + "\n"
                    self.was_entry_modified = True
                self._new_cron_io.write(line)
            else:
                break
        return self._new_cron_io.getvalue()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._cron_io.close()
        return False
