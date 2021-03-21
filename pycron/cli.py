# Command line for crontab entries
import argparse

from python_crontab.cron_argparser import MainMediatorFuncs, UpdateMediatorFuncs
from python_crontab.pycron_enum import SubPyCron, PyCron

args_tuple = ("[int, str]", "[int, str, str]")

parser = argparse.ArgumentParser(
    prog="pycron.cli",
    description="""
    Handles the Python script or module 
    so it will run at some time interval
    """)

group = parser.add_mutually_exclusive_group()

parser.add_argument(PyCron.PY.build_args(),
                    action=MainMediatorFuncs,
                    type=str,
                    required=True,
                    help="path to python interpreter")

parser.add_argument(PyCron.MODULE.build_args(),
                    action="store_true",
                    help="Changes the CRUD switches to accept python module")

group.add_argument(PyCron.INIT.build_args(),
                   action=MainMediatorFuncs,
                   nargs="*",
                   metavar=args_tuple,
                   help=f""" Initialize the cron script with an entry to crontab file with 
                    specified interval in minutes and path to python script [module].""")

group.add_argument(PyCron.INSERT.build_args(),
                   action=MainMediatorFuncs,
                   nargs="*",
                   metavar=args_tuple,
                   help=f""" Inserts a new entry at crontab file with  
                    specified interval in minutes and path to python script [module].""")

group.add_argument(PyCron.DELETE.build_args(),
                   action=MainMediatorFuncs,
                   nargs="*",
                   metavar=args_tuple,
                   help=f""" Removes an entry from crontab file with 
                    specified interval in minutes and path to python script [module].""")

group.add_argument(PyCron.UPDATE.build_args(),
                   action=UpdateMediatorFuncs,
                   nargs="*",
                   metavar=(f"[\"{SubPyCron.OLD.build_args()} int str {SubPyCron.NEW.build_args()} int str\"]",
                            f"[\"{SubPyCron.OLD.build_args()} int str str {SubPyCron.NEW.build_args()} int str str\"]"),
                   help=f"""The interval in minutes and python script path to update. 
                   The arguments must be in the following pattern: 
                   \"--old number path/to/python/(script[module]) [python module name]\"
                   \"--new number path/to/python/(script[module]) [python module name]\". 
                   The double quotation around the arguments is required""")

parser.parse_args()
