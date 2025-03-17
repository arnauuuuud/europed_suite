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
    parser.add_argument("list_name", type=useful_recurring_functions.parse_modes, help = "file name list to append to the waiting list")
    
    args = parser.parse_args()
    return args.list_name
    
    
def append(file_path,line):
    with open(file_path, 'a') as file:
        lock_file(file)
        file.write(line)
        unlock_file(file)

def main(filename_list):
    for filename in filename_list:
        append(waitinglistfile,filename+'\n')

if __name__ == "__main__":
    list_name = argument_parser()
    main(list_name)



