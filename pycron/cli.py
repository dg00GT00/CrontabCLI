# Command line for crontab entries
import argparse

from python_crontab.cron_argparser import MainMediatorFuncs, SubMediatorFuncs
from python_crontab.pycron_enum import SubPyCron, PyCron

args_tuple = ("int", "str")

increment_help = """
    [Case --module, -m specified, this switch should received the 
    absolute python's module path location and the python's module name]
"""

parser = argparse.ArgumentParser(
    prog="pycron.cli",
    description="""
    Sets the location of a Python project 
    entry point and specifies the interval time
    that the script will be ran
    """)

sub_parsers = parser.add_subparsers()

# update_args = sub_parsers.add_parser("update", help="Commands for updating an entry on cron file")
#
# update_args.add_argument(SubPyCron.OLD.build_args(),
#                          action=SubMediatorFuncs,
#                          nargs=len(args_tuple),
#                          required=True,
#                          metavar=args_tuple,
#                          help=f"""The interval in minutes and python script path to update.""")
#
# update_args.add_argument(SubPyCron.NEW.build_args(),
#                          action=SubMediatorFuncs,
#                          nargs=len(args_tuple),
#                          required=True,
#                          metavar=args_tuple,
#                          help=f"""The interval in minutes and python script path to update.""")

module_parser = sub_parsers.add_parser("module", help="Commands for when a python module is specified")

# module_parser.add_argument(PyCron.MODULE.build_args(), "-m",
#                            action="store_true",
#                            help="""Inserts a Python module instead of a Python script""")

group = parser.add_mutually_exclusive_group()

parser.add_argument(PyCron.PY.build_args(),
                    action=MainMediatorFuncs,
                    type=str,
                    required=True,
                    help="python interpreter")

group.add_argument(PyCron.INIT.build_args(),
                   action=MainMediatorFuncs,
                   nargs=len(args_tuple),
                   metavar=args_tuple,
                   help=f""" Put an entry to crontab file with the 
                    specified interval in minutes and the path to python script.""")

group.add_argument(PyCron.INSERT.build_args(),
                   action=MainMediatorFuncs,
                   nargs=len(args_tuple),
                   metavar=args_tuple,
                   help=f""" Inserts a new entry at crontab file with the 
                    specified interval in minutes and the path to python script.""")

group.add_argument(PyCron.DELETE.build_args(),
                   action=MainMediatorFuncs,
                   nargs=len(args_tuple),
                   metavar=args_tuple,
                   help=f""" Removes an entry from crontab file with the 
                    specified interval in minutes and the path to python script.""")

group.add_argument(PyCron.UPDATE.build_args(),
                   action=SubMediatorFuncs,
                   nargs="*",
                   metavar=(f"{SubPyCron.OLD.build_args()} int str", f"{SubPyCron.NEW.build_args()} int str"),
                   help=f"""The interval in minutes and python script path to update. 
                   The arguments must be in the following pattern: 
                   \"--old number path/to/python/script\" \"--new number path/to/python/script\". 
                   The double quotation around the arguments is a must""")

parser.parse_args()
