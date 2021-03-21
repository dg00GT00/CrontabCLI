from argparse import Action, ArgumentParser, Namespace
from threading import Thread, Lock
from typing import Any, Sequence, Text, Tuple, Optional, List, NamedTuple

from python_crontab.build_py_cron import BuildPyCronScript, BuildPyModuleCronScript
from python_crontab.manage_pycron import ManagePyCronScript, ManagePyModuleCronScript
from python_crontab.pycron_enum import PyCron, SubPyCron
from utilities import check_attr

global_lock = Lock()


class UpdateValues(NamedTuple):
    old: List[str]
    new: List[str]


def _parse_update_args(update_args: List[str]) -> UpdateValues:
    """
    Rearrange the update list of parameters
    @param update_args: the list came from update namespace object
    @return: restructured namedtuple
    """
    old_values = ""
    new_values = ""
    for update_arg in update_args:
        if SubPyCron.NEW.build_args() in update_arg:
            new_values = update_arg.split(SubPyCron.NEW.build_args())[1].split()
        else:
            old_values = update_arg.split(SubPyCron.OLD.build_args())[1].split()
    return UpdateValues(old=old_values, new=new_values)


class BindValues(Action):
    """
    Base argument parser class with holds an instance of the manage crontab implementation
    """

    def __init__(self, option_strings: Sequence[Text], dest: Text, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
        self.module = False
        self.cron_manager: Optional[ManagePyCronScript] = None

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any,
                 option_string=None) -> None:
        setattr(namespace, self.dest, values)

        with global_lock:
            if self.module:
                self.cron_manager = ManagePyModuleCronScript(BuildPyModuleCronScript())
            else:
                self.cron_manager = ManagePyCronScript(BuildPyCronScript())

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

        self.cron_manager.interval = values[0]
        self.cron_manager.set_script(values[1])

        if getattr(namespace, str(PyCron.INIT)) is not None:
            self.cron_manager.init_cron()
        elif getattr(namespace, str(PyCron.INSERT)) is not None:
            self.cron_manager.insert_new_cron()
        elif getattr(namespace, str(PyCron.DELETE)) is not None:
            self.cron_manager.remove_cron_entry()
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
        BindValues.__call__(self, parser, namespace, values, option_string)
        self.cron_manager.event.wait()

        update_values = _parse_update_args(getattr(namespace, str(PyCron.UPDATE)))
        self.cron_manager.set_script(update_values.new[1])

        self.cron_manager.set_new_values(update_values.new)
        self.cron_manager.set_old_values(update_values.old)
        self.cron_manager.update_cron()
        self.end_message()


class MainMediatorFuncs(CallInitFuncs, CallMainParserFuncs):
    """
    Manages the action execution order when parsing arguments of the main parser
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any,
                 option_string=None) -> None:
        if check_attr(namespace, str(PyCron.PY)) and isinstance(values, str):
            Thread(target=CallInitFuncs.__call__,
                   args=(self, parser, namespace, values, option_string)).start()
        else:
            Thread(target=CallMainParserFuncs.__call__,
                   args=(self, parser, namespace, values, option_string)).start()


class SubMediatorFuncs(CallInitFuncs, CallSubParserFuncs):
    """
    Manages the action execution order when parsing arguments of the sub parser
    """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any,
                 option_string=None) -> None:
        if check_attr(namespace, str(PyCron.PY)) and isinstance(values, str):
            Thread(target=CallInitFuncs.__call__,
                   args=(self, parser, namespace, values, option_string)).start()
        else:
            Thread(target=CallSubParserFuncs.__call__,
                   args=(self, parser, namespace, values, option_string)).start()
