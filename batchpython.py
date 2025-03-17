#!/usr/local/depot/Python-3.7/bin/python3
from jetlib.misc import BatchRun
import sys
import os
# First argument should be filepath of python file to run in batch
# All additional arguments will be handed to the python file as cmdline arguments
filepath = sys.argv[1]
if '/' not in filepath:
    filepath = f"{os.getcwd()}/{filepath}"

username = 'jzj7540'
print(f'Current username is {username}, if not good, please update it.')

initdir = f"/home/{username}/work/scripts/batchtmpdir/"

runfile_name = filepath.split('/')[-1][:-3]
submitfile_name = runfile_name

runfile_argument = f"python {filepath}"
if len(sys.argv) > 2: # appending possible command line specifiers
    runfile_argument = f"{runfile_argument} {' '.join(sys.argv[2:])}"

runfile_arguments = [runfile_argument]
submitfile_arguments = ["# @ requirements = (Memory = any)\n"]

batch = BatchRun(initdir, runfile_name, submitfile_name, runfile_arguments, submitfile_arguments, cleanup = False, email = True)
batch.submit()
