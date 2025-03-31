#!/usr/local/depot/Python-3.7/bin/python
# /usr/local/depot/Python-3.5.1/bin/python
import argparse
from europed_suite import useful_recurring_functions
import fcntl

username = 'jzj7540'
waitinglistfile = f'/home/{username}/Desktop/waitinglist'

def lock_file(file):
    fcntl.flock(file, fcntl.LOCK_EX)

def unlock_file(file):
    fcntl.flock(file, fcntl.LOCK_UN)

#####################################################################
def argument_parser():
    """Defining comandline parser and returning the arguments"""
    parser = argparse.ArgumentParser(description = "Append file to the waiting list")
    parser.add_argument("folder_name", help = "folder containing the input files to put in the waiting list")
    
    args = parser.parse_args()
    return args.folder_name
    
    
def append(file_path,line):
    with open(file_path, 'a') as file:
        lock_file(file)
        file.write(line)
        unlock_file(file)

def main(folder_name):
    os.chdir(f"{os.environ['EUROPED_DIR']}input/{folder_name}")
    for filename in os. listdir():
        append(waitinglistfile,f'{folder_name}/{filename}\n')

if __name__ == "__main__":
    folder_name = argument_parser()
    main(folder_name)



