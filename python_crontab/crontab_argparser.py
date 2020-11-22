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
        self.cron_manager = ManagePythonCrontabScript()

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
        self.cron_manager.event.wait()
        if getattr(namespace, "init") is not None:
            self.cron_manager.init_crontab(*values)
        elif getattr(namespace, "update") is not None:
            self.cron_manager.update_crontab(*values)
        elif getattr(namespace, "insert") is not None:
            self.cron_manager.insert_new_crontab(*values)
        elif getattr(namespace, "delete") is not None:
            self.cron_manager.remove_crontab_entry(*values)
        print("Done!")


class CallInitFuncs(BindValues):
    """
    Responsible for executing the actions that must be run before any other action
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str,
                 option_string=None) -> None:
        BindValues.__call__(self, parser, namespace, values, option_string)
        self.cron_manager.pycron_builder.set_py_interpreter(values)
        self.cron_manager.event.set()


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
