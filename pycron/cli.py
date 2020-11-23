# Command line for crontab entries
import argparse

from python_crontab.cron_argparser import MainMediatorFuncs, SubMediatorFuncs
from python_crontab.pycron_enum import SubPyCron, PyCron

parser = argparse.ArgumentParser(
    prog="pycron.cli.py",
    description="""
    Sets the location of the JobFinders project 
    entry point and specifies the interval time
    that the script will be ran
    """)

update_parser = parser.add_subparsers(help="Commands for updating an entry on cron file")

update_args = update_parser.add_parser("update")

update_args.add_argument(SubPyCron.OLD.build_args(),
                         action=SubMediatorFuncs,
                         nargs=2,
                         required=True,
                         metavar=("int", "str"),
                         help="The interval in minutes and python script path to update")

update_args.add_argument(SubPyCron.NEW.build_args(),
                         action=SubMediatorFuncs,
                         nargs=2,
                         required=True,
                         metavar=("int", "str"),
                         help="The interval in minutes and python script path to set the update")

group = parser.add_mutually_exclusive_group()

group.add_argument(PyCron.INIT.build_args(),
                   action=MainMediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Put an entry to crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

group.add_argument(PyCron.INSERT.build_args(),
                   action=MainMediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Inserts a new entry at crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

group.add_argument(PyCron.DELETE.build_args(),
                   action=MainMediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Removes an entry from crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

parser.add_argument(PyCron.PY.build_args(),
                    action=MainMediatorFuncs,
                    type=str,
                    required=True,
                    help="python interpreter")

parser.parse_args()
