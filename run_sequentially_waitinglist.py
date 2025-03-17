#!/usr/local/depot/Python-3.7/bin/python
# /usr/local/depot/Python-3.5.1/bin/python

import subprocess
import time
import fcntl

username = 'jzj7540'
print(f'Current username is {username}, if not good, please update it.')

waitinglistfile = f'/home/{username}/Desktop/waitinglist'
launchedlist_file = f'/home/{username}/Desktop/launched'

def lock_file(file):
    fcntl.flock(file, fcntl.LOCK_EX)

def unlock_file(file):
    fcntl.flock(file, fcntl.LOCK_UN)

#####################################################################
def read_and_delete_first_line(file_path):
    with open(file_path, 'r') as file:
        lock_file(file)
        lines = file.readlines()
        unlock_file(file)
    if not lines:
        return None  # File is empty
    first_line = lines[0]

    if first_line == 'pause\n':
        return first_line
    else:
        with open(file_path, 'w') as file:
            lock_file(file)
            file.writelines(lines[1:])
            unlock_file(file)
        return first_line


def append(file_path,line):
    with open(file_path, 'a') as file:
        lock_file(file)
        file.write(line)
        unlock_file(file)


def count_processes_running():
    command = "llq -l | grep {username}.*"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)   
    return len(result.stdout.splitlines())


def launch_and_wait(filename):
    print(f'Launching run with filename: {filename}')
    command = f"/home/{username}/work/europed/europed.py /home/{username}/work/europed/input/{filename} -b"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    time.sleep(600)
    while count_processes_running()>15:
        print("Not enough computing time to launch new runs", end='\r')
        time.sleep(300)  # Check every 300 second  
    print("Available computing time                                       ")
    return True

def main():
    while True:
        filename = read_and_delete_first_line(waitinglistfile)
        while filename is not None and filename != 'pause\n' :
            append(launchedlist_file,filename)
            print(filename[:-1])
            launch_and_wait(filename[:-1])
            filename = read_and_delete_first_line(waitinglistfile)
        if filename is None:
            print('Empty waiting list - wait 1 hour')
            time.sleep(3600)
        elif filename == 'pause\n':
            print('Pause - wait 10 minutes')
            time.sleep(600)


if __name__ == "__main__":
    main()



