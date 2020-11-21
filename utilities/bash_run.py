import subprocess
from collections import namedtuple
from typing import List

BashResults = namedtuple("BashResults", ["return_code", "result"])


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
