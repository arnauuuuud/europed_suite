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
    parser.add_argument("-p", '--pauses', type=useful_recurring_functions.parse_modes, help = "which pause to pop")
    
    args = parser.parse_args()
    return args.list_name,args.pauses
    
def remove_exact_line(filename, exact_line, pauses):
    if pauses == None:
        pauses = []
    # Read the file contents
    with open(filename, 'r+') as file:
        lock_file(file)
        lines = file.readlines()
        if exact_line != 'pause':
            lines_to_put = [line for line in lines if line.strip() != exact_line]
        else:
            count = 0
            lines_to_put = []
            for line in lines:
                if line.strip() != 'pause':
                    lines_to_put.append(line)
                else:
                    if str(count) not in pauses:
                        lines_to_put.append(line)
                    count += 1
        file.seek(0)
        file.truncate()
        file.writelines(lines_to_put)
        unlock_file(file)


def main(filename_list, pauses):
    for filename in filename_list:
        remove_exact_line(waitinglistfile, filename, pauses)

if __name__ == "__main__":
    list_name,pauses = argument_parser()
    main(list_name,pauses)



