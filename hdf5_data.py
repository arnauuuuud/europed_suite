#!/usr/local/depot/Python-3.7/bin/python
# /usr/local/depot/Python-3.5.1/bin/python

from europed_suite import useful_recurring_functions, h5_manipulation
import os
import h5py
import gzip
import tempfile
import glob
import numpy as np
import fcntl

def lock_file(file):
    fcntl.flock(file, fcntl.LOCK_EX)

def unlock_file(file):
    fcntl.flock(file, fcntl.LOCK_UN)

research_dir = os.environ['EUROPED_DIR']+'hdf5'

def find_stored_name(europed_name):
    paths = glob.glob(f'{research_dir}/{europed_name}.h5*', recursive=False)
    print(f'{research_dir}/{europed_name}.h5*')
    too_many_with_name = False
    print(paths)
    if len(paths) == 0:
        raise useful_recurring_functions.CustomError(f"No file found '{europed_name}'")
    elif len(paths) == 1:
        stored_name = paths[0]
    elif len(paths) == 2:
        if paths[0].endswith('.h5.gz') and paths[1].endswith('.h5'):
            stored_name = paths[0]
        elif paths[1].endswith('.h5.gz') and paths[0].endswith('.h5'):
            stored_name = paths[1]
        else:
            too_many_with_name = True
    else:
        too_many_with_name = True

    if too_many_with_name:
        raise useful_recurring_functions.CustomError(f"Too many files finishing with '{europed_name}'")

    return stored_name


def read(europed_name, list_groups):
    zipped = h5_manipulation.decompress_gz(f'{europed_name}.h5.gz')
    with h5py.File(f'{europed_name}.h5', 'r') as hdf5_file:
        # lock_file(hdf5_file)
        temp = hdf5_file
        for group in list_groups:
            temp = temp[group]
        try:
            res = temp[0]
        except AttributeError:
            print(list(temp.keys()))
        # unlock_file(hdf5_file)

    if zipped:
        h5_manipulation.removedoth5(f'{europed_name}.h5')
    return res



def get(europed_name, list_groups):
    zipped = h5_manipulation.decompress_gz(europed_name)
    with h5py.File(f'{europed_name}.h5', 'r') as hdf5_file:
        # lock_file(hdf5_file)
        temp = hdf5_file
        try:
            for group in list_groups:
                temp = temp[group]
            res = temp[0]

        # except KeyError:
        #     res = None
        except AttributeError:
            res = list(temp.keys())
        # unlock_file(hdf5_file)
    if zipped:
        h5_manipulation.removedoth5(europed_name)
    return res

def get_xparam(europed_name, x_parameter):
    zipped = h5_manipulation.decompress_gz(europed_name)
    with h5py.File(f'{europed_name}.h5', 'r') as hdf5_file:
        try:
            n = hdf5_file['input']['steps'][0]
            list_profile = range(n)
        except KeyError:
            # n = len(hdf5_file['scan'])
            list_profile = list(hdf5_file['scan'].keys())
        res = [np.nan for i in list_profile]
        
        for i in list_profile:
            try:
                res[int(i)] = hdf5_file['scan'][str(i)][x_parameter][0]
            except KeyError:
                pass
            except IndexError:
                pass
        # unlock_file(hdf5_file)
    if zipped:
        h5_manipulation.removedoth5(europed_name)
    return res

def get_xparam_with_stability(europed_name, x_parameter):
    zipped = h5_manipulation.decompress_gz(europed_name)
    with h5py.File(f'{europed_name}.h5', 'r') as hdf5_file:
        # lock_file(hdf5_file)
        try:
            n = hdf5_file['input']['steps'][0]
            list_profile = range(n)
        except KeyError:
            # n = len(hdf5_file['scan'])
            list_profile = list(hdf5_file['scan'].keys())
        res = np.zeros(len(list_profile))
        for i in list_profile:
            try:
                test = hdf5_file['scan'][str(i)]['castor']
                res[int(i)] = hdf5_file['scan'][str(i)][x_parameter][0]
            except KeyError:
                pass
        # unlock_file(hdf5_file)
    if zipped:
        h5_manipulation.removedoth5(europed_name)
    return res


    

    # europed_run = glob.glob(pattern)[0]

    # if europed_run.endswith(".gz"):
    #     with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    #         with gzip.open(europed_run, 'rb') as gz_file:
    #             tmp_file.write(gz_file.read())
    #             tmp_file_name = tmp_file.name
    #     temp = True
    # else:
    #     tmp_file_name = europed_run
    #     temp = False

    # with h5py.File(tmp_file_name, 'r') as hdf5_file:
    #     temp = hdf5_file
    #     for group in list_groups:
    #         print(group, end='/')
    #         temp = temp[group]
    #     print()
    #     print(temp[0])



    # os.remove(tmp_file_name)



if __name__ == '__main__':
    main()