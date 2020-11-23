import os
from argparse import Namespace
from typing import NoReturn

from exceptions import MinOutOfRangeException
from utilities.bash_run import run_bash_cmd

"""
Collection of utilities functions and classes which does not have necessarily relation to each other  
"""


def time_constraints(time: str) -> NoReturn:
    """
    Checks if an input time is between defined constraints
    :param time: the input time to check for
    """
    if int(time) < 0 or int(time) > 59:
        raise MinOutOfRangeException


def generate_new_crontab(new_crontab: str) -> None:
    """
    Generate a new crontab entry and insert it into the cron file
    :param new_crontab: the already formatted crontab entry
    """
    echo = run_bash_cmd(["echo", new_crontab], show_output=True).result
    run_bash_cmd(["crontab"], stdin=echo)


def check_source_existence(path: str) -> NoReturn:
    """
    Checks if the provide path exists
    :param path: the path to check existence for
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")


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


def check_attr(namespace: Namespace, attr: str) -> bool:
    """
    Checks if a namespace has an attribute and if its value is different from None
    :param namespace: the namespace to check through
    :param attr: the attribute name which will be check for
    """
    if hasattr(namespace, attr) and getattr(namespace, attr) is None:
        return True
    return False
