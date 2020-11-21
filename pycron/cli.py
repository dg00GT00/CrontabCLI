# Command line for crontab entries
import argparse

from python_crontab.crontab_argparser import MediatorFuncs

parser = argparse.ArgumentParser(
    description="""
    Sets the location of the JobFinders project 
    entry point and specifies the interval time
    that the script will be ran
    """,
)

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("--init", "-i",
                   action=MediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Put an entry to crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

group.add_argument("--update", "-u",
                   action=MediatorFuncs,
                   nargs=2,
                   metavar=("int", "str"),
                   help=""" Update the entry at crontab file with the 
                    specified interval in minutes and
                    the path to python script """)

parser.add_argument("--py",
                    action=MediatorFuncs,
                    type=str,
                    required=True,
                    help="python interpreter")

parser.parse_args()
