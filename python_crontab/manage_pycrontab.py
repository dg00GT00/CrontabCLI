import io
import re
import threading

from env import USER
from python_crontab.build_py_crontab import BuildPythonCrontabScript
from utilities import singleton, check_pkg_existence, run_bash_cmd, generate_new_crontab


@singleton
class ManagePythonCrontabScript(BuildPythonCrontabScript):
    """
    Manages the insertion and updating of the python script into cron
    """

    def __init__(self):
        super().__init__()
        check_pkg_existence()
        self.event = threading.Event()

    def init_crontab(self):
        """
        Initialize a cron entry with the python scrip if one not already exist
        """
        if run_bash_cmd(["crontab", "-l"]).return_code != 0:
            print(f"Generating a new crontab for {USER} user...")
            generate_new_crontab(self.build_script().strip())
        else:
            print(f"{USER} user already has a crontab entry. Calling update function...")
            self.update_crontab()

    def update_crontab(self):
        """
        Update a cron python entry with new time values
        """
        if run_bash_cmd(["crontab", "-l"]).return_code == 0:
            print("Updating the crontab entry...")
            interval, py_script = self.interval_script
            escape = re.escape(py_script)
            cron_io: io.TextIOWrapper = run_bash_cmd(["crontab", "-l"], show_output=True).result
            cron_script = cron_io.read()
            cron_io.close()
            new_script = re.sub(fr"(?<=\*/)\d+(?=(?:\s\*)+\s+{self.py_interpreter}\d*\.*\d*\s*{escape})", interval,
                                cron_script, count=1)
            run_bash_cmd(["crontab", "-r"])
            generate_new_crontab(new_script.strip())
        else:
            print(f"No entry found. Initializing the a crontab entry for {USER} user...")
            self.init_crontab()
