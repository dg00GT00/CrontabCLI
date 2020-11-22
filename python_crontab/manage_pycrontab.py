import threading

from env import USER
from exceptions import NoCronEntryFound
from python_crontab.build_py_crontab import BuildPythonCrontabScript
from utilities import singleton, check_pkg_existence, generate_new_crontab
from utilities.crontab_script_manager import CrontabScriptManager


@singleton
class ManagePythonCrontabScript:
    """
    Manages the insertion and updating of the python script into cron
    """

    def __init__(self):
        super().__init__()
        check_pkg_existence()
        self.event = threading.Event()
        self.pycron_builder = BuildPythonCrontabScript()

    def _update_py_specs(self, interval: str, script: str) -> None:
        self.pycron_builder.set_interval_script(interval, script)

    def init_crontab(self, interval: str, script: str) -> None:
        """
        Initialize a cron entry with the python scrip if one not already exist
        """
        self._update_py_specs(interval, script)
        with CrontabScriptManager(self.pycron_builder) as c:
            if not c.some_entry_exists:
                print(f"Generating a new crontab for {USER} user...")
                generate_new_crontab(c.crontab_gen.build_cron_script())
            else:
                print(f"{USER} user already has a crontab entry. Calling update function...")
                self.update_crontab(interval, script)

    def update_crontab(self, interval: str, script: str) -> None:
        """
        Update a cron python entry with new time values
        """
        self._update_py_specs(interval, script)
        with CrontabScriptManager(self.pycron_builder) as c:
            if c.some_entry_exists:
                print("Updating the crontab entry...")
                new_script = c.update_crontab(self.pycron_builder.py_interpreter)
                generate_new_crontab(new_script)
            else:
                print(f"No entry found. Initializing the a crontab entry for {USER} user...")
                self.init_crontab(interval, script)

    def insert_new_crontab(self, interval: str, script: str) -> None:
        self._update_py_specs(interval, script)
        with CrontabScriptManager(self.pycron_builder) as c:
            if c.some_entry_exists:
                print("Inserting a new crontab entry...")
                new_script = c.insert_new_crontab()
                generate_new_crontab(new_script)
            else:
                print(f"No entry found. Initializing the a crontab entry for {USER} user...")
                self.init_crontab(interval, script)

    def remove_crontab_entry(self, interval: str, script: str) -> None:
        self._update_py_specs(interval, script)
        with CrontabScriptManager(self.pycron_builder) as c:
            if c.some_entry_exists:
                print("Removing the crontab entry...")
                new_script = c.remove_crontab_entry()
                generate_new_crontab(new_script)
                if not c.was_entry_modified:
                    print("No entry found to be deleted with provided parameters. Cron file not touched!")
            else:
                raise NoCronEntryFound
