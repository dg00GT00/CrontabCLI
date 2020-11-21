import abc
import argparse
import io
import os
import re
import subprocess
import threading
from collections import namedtuple
from functools import wraps
from typing import Final, Callable, Any, List, Tuple, Sequence, Text, Type, NoReturn, Union

USER: Final[str] = os.getenv('USER', 'unknown')
BashResults = namedtuple("BashResults", ["return_code", "result"])


# Command line for crontab entries
# TODO: Split granular functionality of this module to other modules

class MinOutOfRangeException(Exception):
    """
    Exception to crontab minutes range
    """
    def __str__(self):
        return "The minutes field must be encompassed from 0 up to 59"


class ICrontabEntry(abc.ABC):
    """
    Interface for setting a python script entry through crontab command
    """
    @abc.abstractmethod
    def set_interval_script(self, interval: str, py_script: str) -> None:
        """Sets the interval and the python script path"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_py_interpreter(self, py_interpreter: str) -> None:
        """Sets the path for python interpreter"""
        raise NotImplementedError


def check_args_integrity(func: Callable[..., Any]) -> Union[Callable[..., Any], NoReturn]:
    """
    An decorator aggregator of checks with the view of confirming the consistence of arguments
    passed in the function
    :param func: the function to check the arguments of
    :return: the function wrapped with the checks
    """
    def inner_check(interval: str, py_script: str) -> NoReturn:
        check_pyscript_existence(py_script)
        if int(interval) < 0 or int(interval) > 59:
            raise MinOutOfRangeException

    @wraps(func)
    def main_func(*args):
        if isinstance(args[0], ICrontabEntry):
            inner_check(*args[1:])
        else:
            inner_check(*args)
        func(*args)

    return main_func


def run_bash_cmd(commands: List[str], *, show_output: bool = False, **kwargs) -> BashResults:
    """
    Run a list of bash command
    :param commands: the list of commands for running through bash
    :param show_output: if the output of the command is redirect to stdout
    :param kwargs: generic parameter to pass in to bash
    :return: an object which contains the bash result and the return code
    """
    pipe = subprocess.PIPE if show_output else subprocess.DEVNULL
    completed = subprocess.Popen(commands, stdout=pipe, stderr=subprocess.STDOUT, encoding="utf-8", **kwargs)
    completed.wait()
    return BashResults(return_code=completed.returncode, result=completed.stdout)


def generate_new_crontab(new_crontab: str) -> None:
    """
    Generate a new crontab entry and insert it into the cron file
    :param new_crontab: the already formatted crontab entry
    """
    echo = run_bash_cmd(["echo", new_crontab], show_output=True).result
    run_bash_cmd(["crontab"], stdin=echo)


def check_pyscript_existence(py_script: str) -> NoReturn:
    """
    Checks there is a python script defined by a provide path
    :param py_script: the python script path to check for existence
    """
    if not os.path.exists(py_script):
        raise FileNotFoundError(f"{py_script} not found")


def check_pkg_existence() -> None:
    """
    Check if the cron command exists on the OS. Case not, it is installed
    alongside with its dependencies (postfix)
    """
    check_crontab = run_bash_cmd(["which", "crontab"]).return_code != 0
    check_postfix = run_bash_cmd(["which", "postfix"]).return_code != 0
    if check_crontab:
        print("Installing cron...")
        os.system("sudo apt install cron")
    if check_postfix:
        print("Installing postfix...")
        os.system("sudo apt install postfix")


def singleton(_class: Type[ICrontabEntry]) -> Callable[..., ICrontabEntry]:
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


class BuildPythonCrontabScript(ICrontabEntry):
    """
    Builds the formatted python script entry to insertion on cron by
    crontab command
    """
    def __init__(self):
        self.py_interpreter = ""
        self.interval_script: Tuple[str, str] = ("", "")

    def set_py_interpreter(self, py_interpreter: str) -> None:
        check_pyscript_existence(py_interpreter)
        self.py_interpreter = py_interpreter

    @check_args_integrity
    def set_interval_script(self, interval: str, py_script: str) -> None:
        self.interval_script = (interval, py_script)

    def build_script(self) -> str:
        interval, py_script = self.interval_script
        return f"*/{interval} * * * * {self.py_interpreter} {py_script}"


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


class BindValues(argparse.Action):
    """
    Base argument parser class with holds an instance of the manage crontab implementation
    """
    def __init__(self, option_strings: Sequence[Text], dest: Text, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
        self.manage_crontab = ManagePythonCrontabScript()

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,
                 option_string=None) -> None:
        setattr(namespace, self.dest, values)


class CallExecFuncs(BindValues):
    """
    Responsible for executing the actions for managing the crontab entries
    """
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Tuple[str, str],
                 option_string=None) -> None:
        BindValues.__call__(self, parser, namespace, values, option_string)
        self.manage_crontab.set_interval_script(*values)
        self.manage_crontab.event.wait()
        if getattr(namespace, "init") is not None:
            self.manage_crontab.init_crontab()
        elif getattr(namespace, "update") is not None:
            self.manage_crontab.update_crontab()
        print("Done!")


class CallInitFuncs(BindValues):
    """
    Responsible for executing the actions that must be run before any other action
    """
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: str,
                 option_string=None) -> None:
        BindValues.__call__(self, parser, namespace, values, option_string)
        self.manage_crontab.set_py_interpreter(values)
        self.manage_crontab.event.set()


class MediatorFuncs(CallInitFuncs, CallExecFuncs):
    """
    Manages the action execution order when parsing arguments
    """
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,
                 option_string=None) -> None:
        if option_string == "--py":
            threading.Thread(target=CallInitFuncs.__call__,
                             args=(self, parser, namespace, values, option_string)).start()
        else:
            threading.Thread(target=CallExecFuncs.__call__,
                             args=(self, parser, namespace, values, option_string)).start()


parser = argparse.ArgumentParser(
    description="""
    Sets the location of the JobFinders project 
    entry point and specifies the interval time
    that the script will be ran
    """,
)

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("--init", "-i",
                   action=MediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Put an entry to crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

group.add_argument("--update", "-u",
                   action=MediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Update the entry at crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

parser.add_argument("--py",
                    action=MediatorFuncs,
                    type=str,
                    required=True,
                    help="python interpreter")

parser.parse_args()
