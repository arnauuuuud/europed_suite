import os, gzip, re, shutil
from europed_suite import useful_recurring_functions
import h5py
import fcntl

def lock_file(file):
    fcntl.flock(file, fcntl.LOCK_EX)

def unlock_file(file):
    fcntl.flock(file, fcntl.LOCK_UN)




def get_latest_version(original_name):
    foldername = f"{os.environ['EUROPED_DIR']}hdf5"
    os.chdir(foldername)
    pattern = re.compile(rf'{original_name}_(\d+)_.*\.h5\.gz')
    with os.scandir() as entries:
        files = [entry.name for entry in entries if entry.name.startswith(original_name)]
    latest_version_number = 0
    for filename in files:
        match = pattern.match(filename)
        if match:
            version_number = int(match.group(1))
            if version_number > latest_version_number:
                latest_version_number = version_number
    return latest_version_number


def removedoth5(filename):
    foldername = f"{os.environ['EUROPED_DIR']}hdf5"
    os.chdir(foldername)
    os.remove(f'{filename}.h5')

def decompress_gz(filename):
    foldername = f"{os.environ['EUROPED_DIR']}hdf5"
    os.chdir(foldername)

    if os.path.isfile(f'{filename}.h5'):
        return False

    with gzip.open(f'{filename}.h5.gz', 'rb') as f_in, open(f'{filename}.h5', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    return True

def compress_to_gz(filename):
    foldername = f"{os.environ['EUROPED_DIR']}hdf5"
    os.chdir(foldername)
    with open(f'{filename}.h5', 'rb') as f_in, gzip.open(f'{filename}.h5.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    removedoth5(filename)


def get_data(filename, list_groups):
    zipped = decompress_gz(filename)
    with h5py.File(f'{filename}.h5', 'r') as hdf5_file:
        # lock_file(hdf5_file)
        temp = hdf5_file
        for group in list_groups:
            # print(group, end='/')
            temp = temp[group]
        res = temp[0]
        # unlock_file(hdf5_file)
    if zipped:
        removedoth5(filename)
    return res

def get_data_decrompressed(filename, list_groups):
    with h5py.File(f'{filename}.h5', 'r') as hdf5_file:
        # lock_file(hdf5_file)
        temp = hdf5_file
        for group in list_groups:
            # print(group, end='/')
            temp = temp[group]
        res = temp[0]
        # unlock_file(hdf5_file)
    return res


def find_profile_with_delta_name(filename, delta):
    foldername = f"{os.environ['EUROPED_DIR']}hdf5"
    os.chdir(foldername)
    res = None
    with h5py.File(f'{filename}.h5', 'r') as h5file:
        # lock_file(h5file)
        for profile in h5file['scan'].keys():
            if abs(round((h5file['scan'][profile]['delta'][0]),5) - delta) < 0.0001:
                res = profile
        if res == None:
            # unlock_file(h5file)

            raise useful_recurring_functions.CustomError(f'No profile in {h5file} with the given delta {delta} - discrepancy between the delta list from the hdf5, and the different delta of each profile')
        # unlock_file(h5file)
    return res

def find_profile_with_delta(filename, delta):
    zipped = decompress_gz(filename)
    foldername = f"{os.environ['EUROPED_DIR']}hdf5"
    os.chdir(foldername)
    res = None
    with h5py.File(f'{filename}.h5', 'r') as h5file:
        # lock_file(h5file)
        for profile in h5file['scan'].keys():
            if abs(round((h5file['scan'][profile]['delta'][0]),5) - delta) < 0.0001:
                res = profile

        if res == None:
            # unlock_file(h5file)
            raise useful_recurring_functions.CustomError(f'No profile in {h5file} with the given delta {delta} - discrepancy between the delta list from the hdf5, and the different delta of each profile')
        # unlock_file(h5file)
    if zipped:
        removedoth5(filename)
    return res


def find_profile_with_delta_file(h5file, delta):
    # lock_file(h5file)
    res = None
    for profile in h5file['scan'].keys():
        if abs(round((h5file['scan'][profile]['delta'][0]),5) - delta) < 0.0001:
            res = profile

    if res == None:
        # unlock_file(h5file)
        raise useful_recurring_functions.CustomError(f'No profile in {h5file} with the given delta {delta} - discrepancy between the delta list from the hdf5, and the different delta of each profile')
    # unlock_file(h5file)
    return res

def find_profile_with_betaped_file(h5file, delta):
    # lock_file(h5file)
    res = None
    for profile in h5file['scan'].keys():
        if abs(round((h5file['scan'][profile]['betaped'][0]),5) - delta) < 0.0001:
            res = profile

    if res == None:
        # unlock_file(h5file)
        raise useful_recurring_functions.CustomError(f'No profile in {h5file} with the given betaped {delta} - discrepancy between the betaped list from the hdf5, and the different betaped of each profile')
    # unlock_file(h5file)
    return res