import threading
from argparse import Action, ArgumentParser, Namespace
from typing import Any, Sequence, Text, Tuple

from python_crontab.manage_pycron import ManagePythonCronScript
from utilities import check_attr


class BindValues(Action):
    """
    Base argument parser class with holds an instance of the manage crontab implementation
    """

    def __init__(self, option_strings: Sequence[Text], dest: Text, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
        self.cron_manager = ManagePythonCronScript()

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any,
                 option_string=None) -> None:
        setattr(namespace, self.dest, values)

    def end_message(self):
        if self.cron_manager.successfully_command:
            print("Done!")


class CallMainParserFuncs(BindValues):
    """
    Responsible for executing the actions for managing the crontab entries
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Tuple[str, str],
                 option_string=None) -> None:
        BindValues.__call__(self, parser, namespace, values, option_string)
        self.cron_manager.event.wait()
        if getattr(namespace, "init") is not None:
            self.cron_manager.init_cron(*values)
        elif getattr(namespace, "insert") is not None:
            self.cron_manager.insert_new_cron(*values)
        elif getattr(namespace, "delete") is not None:
            self.cron_manager.remove_cron_entry(*values)
        self.end_message()


class CallInitFuncs(BindValues):
    """
    Responsible for executing the actions that must be run before any other action
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str,
                 option_string=None) -> None:
        BindValues.__call__(self, parser, namespace, values, option_string)
        self.cron_manager.pycron_builder.set_py_interpreter(values)
        self.cron_manager.event.set()


class CallSubParserFuncs(BindValues):

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string=None) -> None:
        super().__call__(parser, namespace, values, option_string)
        self.cron_manager.event.wait()
        if self.dest == "new":
            self.cron_manager.set_new_values(getattr(namespace, "new"))
        elif self.dest == "old":
            self.cron_manager.set_old_values(getattr(namespace, "old"))
        self.cron_manager.update_cron()
        self.end_message()


class MainMediatorFuncs(CallInitFuncs, CallMainParserFuncs):
    """
    Manages the action execution order when parsing arguments of the main parser
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any,
                 option_string=None) -> None:
        if check_attr(namespace, "py"):
            threading.Thread(target=CallInitFuncs.__call__,
                             args=(self, parser, namespace, values, option_string)).start()
        else:
            threading.Thread(target=CallMainParserFuncs.__call__,
                             args=(self, parser, namespace, values, option_string)).start()


class SubMediatorFuncs(CallInitFuncs, CallSubParserFuncs):
    """
    Manages the action execution order when parsing arguments of the sub parser
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any,
                 option_string=None) -> None:
        if check_attr(namespace, "py"):
            threading.Thread(target=CallInitFuncs.__call__,
                             args=(self, parser, namespace, values, option_string)).start()
        else:
            if check_attr(namespace, "new") or check_attr(namespace, "old"):
                threading.Thread(target=CallSubParserFuncs.__call__,
                                 args=(self, parser, namespace, values, option_string)).start()
