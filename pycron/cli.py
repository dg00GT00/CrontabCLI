# Command line for crontab entries
import argparse

from python_crontab.cron_argparser import MainMediatorFuncs, SubMediatorFuncs

parser = argparse.ArgumentParser(
    prog="pycron.cli.py",
    description="""
    Sets the location of the JobFinders project 
    entry point and specifies the interval time
    that the script will be ran
    """)

update_parser = parser.add_subparsers(help="Commands for updating an entry on cron file")

update_args = update_parser.add_parser("update")

update_args.add_argument("--old",
                         action=SubMediatorFuncs,
                         nargs=2,
                         required=True,
                         metavar=("int", "str"),
                         help="The interval in minutes and python script path to update")

update_args.add_argument("--new",
                         action=SubMediatorFuncs,
                         nargs=2,
                         required=True,
                         metavar=("int", "str"),
                         help="The interval in minutes and python script path to set the update")

group = parser.add_mutually_exclusive_group()

group.add_argument("--init", "-i",
                   action=MainMediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Put an entry to crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

group.add_argument("--update", "-u",
                   action=MainMediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Update the entry at crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

group.add_argument("--insert",
                   action=MainMediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Inserts a new entry at crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

group.add_argument("--delete", "-d",
                   action=MainMediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Removes an entry from crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

parser.add_argument("--py",
                    action=MainMediatorFuncs,
                    type=str,
                    required=True,
                    help="python interpreter")

parser.parse_args()
