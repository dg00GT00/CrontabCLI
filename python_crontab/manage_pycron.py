import threading
from functools import wraps
from typing import List, Tuple, Type, Callable

from environment import USER
from exceptions import MinOutOfRangeException
from python_crontab.build_py_cron import BuildPythonCronScript
from python_crontab.icron_entry import ICronEntry
from utilities import check_pkg_existence, generate_new_crontab
from utilities.cron_script_manager import CronScriptManager


def _singleton(_class: Type[ICronEntry]) -> Callable[..., ICronEntry]:
    """
    Decorator that grants a class singleton
    :param _class: the class to hold the singleton
    :return: always the same class instance
    """
    instance = None

    @wraps(_class)
    def inner_sing():
        nonlocal instance
        if instance is None:
            instance = _class()
        return instance

    return inner_sing


def _error_wrapper(func: Callable[..., None]) -> Callable[..., None]:
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except (MinOutOfRangeException, FileNotFoundError) as e:
            print(e)

    return inner


class UpdatePycronValues:
    """
    Holds the old and new pycron came from cron file
    """

    def __init__(self):
        self.old_pycron_values: List[str] = []
        self.new_pycron_values: List[str] = []
        self.ready_to_update = False

    def set_old_values(self, py_cron_value: List[str]) -> None:
        self.old_pycron_values = py_cron_value
        self.ready_to_update = True if len(self.new_pycron_values) != 0 else False

    def set_new_values(self, py_cron_value: List[str]) -> None:
        self.new_pycron_values = py_cron_value
        self.ready_to_update = True if len(self.old_pycron_values) != 0 else False


@_singleton
class ManagePythonCronScript(UpdatePycronValues):
    """
    Manages the insertion and updating of the python script into cron
    """

    def __init__(self):
        check_pkg_existence()
        UpdatePycronValues.__init__(self)
        self.event = threading.Event()
        self.successfully_command = False
        self.pycron_builder = BuildPythonCronScript()

    def _update_py_specs(self, interval: str, script: str) -> None:
        """
        Update the values of interval and python script in the python crontab builder
        :param interval: the interval to update
        :param script: the python script to update
        """
        self.pycron_builder.interval = interval
        self.pycron_builder.script = script

    def _pycron_update_builder(self) -> Tuple[str, str]:
        """
        Builds the old and new python script formatted to cron entry
        :return: a tuple with the formatted python scripts
        """
        self._update_py_specs(*self.old_pycron_values)
        old_pycron = self.pycron_builder.build_cron_script()
        self._update_py_specs(*self.new_pycron_values)
        new_pycron = self.pycron_builder.build_cron_script()
        return old_pycron, new_pycron

    @_error_wrapper
    def init_cron(self, interval: str, script: str) -> None:
        self._update_py_specs(interval, script)
        with CronScriptManager(self.pycron_builder) as c:
            if not c.some_entry_exists:
                print(f"Generating a new cron for {USER} user...")
                generate_new_crontab(c.crontab_gen.build_cron_script())
                self.successfully_command = True
            else:
                print(f"{USER} user already has a cron entry. Call the 'update' command to alter existent entries ")

    @_error_wrapper
    def update_cron(self) -> None:
        if self.ready_to_update:
            with CronScriptManager(self.pycron_builder) as c:
                if c.some_entry_exists:
                    print("Updating the cron entry...")
                    old_pycron, new_pycron = self._pycron_update_builder()
                    new_script = c.update_cron(old_pycron, new_pycron)
                    generate_new_crontab(new_script)
                    if not c.was_entry_modified:
                        print("No correspondent cron entry found to be updated")
                        return
                    self.successfully_command = True
                else:
                    print("No cron entry found. Initialized a cron entry with '--init' or '--insert' flags on cli")

    @_error_wrapper
    def insert_new_cron(self, interval: str, script: str) -> None:
        self._update_py_specs(interval, script)
        with CronScriptManager(self.pycron_builder) as c:
            if c.some_entry_exists:
                print("Inserting a new cron entry...")
                new_script = c.insert_new_cron()
                generate_new_crontab(new_script)
                if c.was_entry_modified:
                    print("This cron entry already exists")
                    return
                self.successfully_command = True
            else:
                print(f"No entry found. Initializing the a cron entry for {USER} user...")
                self.init_cron(interval, script)

    @_error_wrapper
    def remove_cron_entry(self, interval: str, script: str) -> None:
        self._update_py_specs(interval, script)
        with CronScriptManager(self.pycron_builder) as c:
            if c.some_entry_exists:
                print("Removing the cron entry...")
                new_script = c.remove_cron_entry()
                generate_new_crontab(new_script)
                if not c.was_entry_modified:
                    print("No entry found to be deleted with provided parameters")
                    return
                self.successfully_command = True
            else:
                print("The cron file is empty. Nothing to be deleted")
