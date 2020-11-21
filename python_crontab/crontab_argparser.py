import threading
from argparse import Action, ArgumentParser, Namespace
from typing import Any, Sequence, Text, Tuple

from python_crontab.manage_pycrontab import ManagePythonCrontabScript


class BindValues(Action):
    """
    Base argument parser class with holds an instance of the manage crontab implementation
    """

    def __init__(self, option_strings: Sequence[Text], dest: Text, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
        self.manage_crontab = ManagePythonCrontabScript()

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any,
                 option_string=None) -> None:
        setattr(namespace, self.dest, values)


class CallExecFuncs(BindValues):
    """
    Responsible for executing the actions for managing the crontab entries
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Tuple[str, str],
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

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str,
                 option_string=None) -> None:
        BindValues.__call__(self, parser, namespace, values, option_string)
        self.manage_crontab.set_py_interpreter(values)
        self.manage_crontab.event.set()


class MediatorFuncs(CallInitFuncs, CallExecFuncs):
    """
    Manages the action execution order when parsing arguments
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any,
                 option_string=None) -> None:
        if option_string == "--py":
            threading.Thread(target=CallInitFuncs.__call__,
                             args=(self, parser, namespace, values, option_string)).start()
        else:
            threading.Thread(target=CallExecFuncs.__call__,
                             args=(self, parser, namespace, values, option_string)).start()
