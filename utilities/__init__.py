import os
from argparse import Namespace
from functools import wraps
from typing import Callable, Any, Union, NoReturn, Type

from python_crontab.icron_entry import ICronEntry
from utilities.bash_run import run_bash_cmd

"""
Collection of utilities functions and classes which does not have necessarily relation to each other  
"""


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
            print("The minutes field must be encompassed from 0 up to 59")

    @wraps(func)
    def main_func(*args):
        if isinstance(args[0], ICronEntry):
            inner_check(*args[1:])
        else:
            inner_check(*args)
        func(*args)

    return main_func


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


def singleton(_class: Type[ICronEntry]) -> Callable[..., ICronEntry]:
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


def check_attr(namespace: Namespace, attr: str) -> bool:
    """
    Checks if a namespace has an attribute and if its value is different from None
    :param namespace: the namespace to check through
    :param attr: the attribute name which will be check for
    """
    if hasattr(namespace, attr) and getattr(namespace, attr) is None:
        return True
    return False
