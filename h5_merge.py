#!/usr/local/depot/Python-3.7/bin/python
# /usr/local/depot/Python-3.5.1/bin/python

from europed_suite import europed_analysis, h5_manipulation, useful_recurring_functions
import argparse
import numpy as np
import os, h5py, shutil

def argument_parser():
    """Defining comandline parser and returning the arguments"""
    parser = argparse.ArgumentParser(description = "Merge two results of runs together")
    parser.add_argument("original_name", help = "name of the original run")
    parser.add_argument("extension_name", help = "name of the extenstion run")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r',"--replace", action = 'store_const', const = 'replace', default='ignore', dest = 'option', help = "")

    parser.add_argument("--modes", "-n", type=useful_recurring_functions.parse_modes, help= "list of modes (comma-separated)")
    parser.add_argument('--fixed_width', '-f', action='store_const', const=True, dest='is_fixed_width', default=False)
    parser.add_argument('--mishka', '-m', action='store_const', const=True, dest='mishka', default=False)

    parser.add_argument("--deltas", "-d", type=useful_recurring_functions.parse_delta, help= "list of deltas (comma-separated), or delta_min and delta_max (dash-separated - steps 0.002)")

    args = parser.parse_args()

    return args.original_name, args.extension_name, args.option, args.modes, args.deltas, args.is_fixed_width, args.mishka


def new_name_for_original_file(original_name, extension_name, option):
    latest_version = h5_manipulation.get_latest_version(original_name)
    this_version = latest_version+1
    new_name = f"{original_name}_{this_version}_beforemerging_{option}_with_{extension_name}"
    return new_name

def copy_original_file(original_name, extension_name, option):
    foldername = f"{os.environ['EUROPED_DIR']}hdf5"
    os.chdir(foldername)
    new_name = new_name_for_original_file(original_name, extension_name, option)
    if os.path.exists(foldername+new_name):
        raise useful_recurring_functions.CustomError('the new name for the original file already exists')
    h5_manipulation.decompress_gz(original_name)
    shutil.copy(original_name +'.h5', new_name +'.h5')
    h5_manipulation.compress_to_gz(new_name)
    print(f'    New name for the old version of the file: {new_name}')


def merge_single_profile(original_file, extension_file, modes, delta, is_fixed_width, mishka):

    stability_code = 'mishka' if mishka else 'castor'

    if not is_fixed_width:
        profile_original = h5_manipulation.find_profile_with_delta_file(original_file,delta)
        profile_extension = h5_manipulation.find_profile_with_delta_file(extension_file,delta)
    else:
        profile_original = h5_manipulation.find_profile_with_betaped_file(original_file,delta)
        profile_extension = h5_manipulation.find_profile_with_betaped_file(extension_file,delta)        
    if modes is None:
        modes = ['1','2','3','4','5','7','10','20','30','40','50']
    
    for n in modes:
        try:
            del original_file['scan'][profile_original][stability_code][str(n)]
        except KeyError:
            print(f'Original profile with given delta {delta} does not have results for n: {n}')
        try:
            new_group = extension_file['scan'][profile_extension][stability_code][str(n)]
            try:
                original_file['scan'][profile_original][stability_code].create_group(str(n))
            except KeyError:
                original_file['scan'][profile_original].create_group(stability_code)
                original_file['scan'][profile_original][stability_code].create_group(str(n))
            for key in new_group.keys():
                new_group.copy(key, original_file['scan'][profile_original][stability_code][str(n)])
            print(f'Delta {delta} n {n}, results copied')
        except KeyError as e:
            print(str(e))



def merge(original_name, extension_name, option, modes, deltas_to_put, is_fixed_width, mishka):

    stability_code = 'mishka' if mishka else 'castor'

    with h5py.File(f'{original_name}.h5', 'a') as original_file, h5py.File(f'{extension_name}.h5', 'r') as extension_file:
        original_steps = int(original_file['input']['steps'][0])
        count_new_profile = 1
        original_n = [int(i) for i in original_file['input']['n'][0].decode('utf-8').split(',')]
        new_n = [int(mode) for mode in modes]

        if not is_fixed_width:
            try:
                deltas_original = original_file['input']['delta']
            except KeyError:
                deltas_original = europed_analysis.get_x_parameter(original_name, 'delta')
        else:
            try:
                deltas_original = original_file['input']['betaped']
            except KeyError:
                deltas_original = europed_analysis.get_x_parameter(original_name, 'betaped')
    
        new_delta_in_original = []

        for key in extension_file['scan'].keys():
            letsadd = False
            profile = key
            new_group = extension_file['scan'][profile]
            delta_extension = round(float(new_group['delta'][0]),5) if not is_fixed_width else round(float(new_group['betaped'][0]),5)

            # if delta is not in the list of interesting deltas, pass
            if all(abs(delta_extension-delta)>0.0001 for delta in deltas_to_put):
                print(delta_extension)
                print(deltas_to_put)
                print('yessss')
                continue

            # if delta is already in the original file
            elif any(abs(delta_extension-delta)<=0.0001 for delta in deltas_original):
                try:
                    if option == 'replace':
                        merge_single_profile(original_file, extension_file, modes, delta_extension, is_fixed_width, mishka)
                except useful_recurring_functions.CustomError:
                    print('letsadddd')
                    letsadd = True

            # if delta should be added to the original file
            else:
                print('add')
                letsadd = True
            
            if letsadd:
                name_new_profile = str(original_steps + count_new_profile)
                
                count_new_profile += 1
                original_file['scan'].create_group(name_new_profile)
                for key in new_group.keys():
                    new_group.copy(key, original_file['scan'][name_new_profile])
                    # try:
                    #     del original_file['scan'][name_new_profile][stability_code]
                    # except KeyError:
                    #     print('No CASTOR results in the new file')

                    # original_file['scan'][name_new_profile].create_group(stability_code)
                    # new_group_castor = new_group[stability_code]
                    # for mode in new_group_castor.keys():
                    #     if int(mode) in modes:
                    #         new_group_castor.copy(mode, original_file['scan'][name_new_profile][stability_code])

                    

                new_delta_in_original.append(delta_extension)

                print(f"Took profile {profile}, delta {round(float(new_group['delta'][0]),5)} and copied it under name '{name_new_profile}' in file {original_name}")
        
        new_steps = str(original_steps+count_new_profile)
        new_steps_encoded = new_steps.encode('utf-8')
        new_steps_encoded = int(new_steps)
        del original_file['input']['steps']
        original_file['input'].create_dataset('steps', data = [new_steps_encoded])
        try:
            if not is_fixed_width:
                del original_file['input']['delta']
            else:
                del original_file['input']['betaped']
        except KeyError:
            pass
        updated_delta = np.concatenate((deltas_original,new_delta_in_original))
        if not is_fixed_width:
            original_file['input'].create_dataset('delta', data = updated_delta)
        else:
            original_file['input'].create_dataset('betaped', data = updated_delta)

        updated_n = sorted(list(set(np.concatenate((original_n,new_n)))))
        updated_n = ','.join(map(str, updated_n))
        updated_n_encoded = updated_n.encode('utf-8')
        del original_file['input']['n']
        original_file['input'].create_dataset('n', data = [updated_n_encoded])

        print(f'Updated number of steps in {original_name}: {new_steps}')
        print(f'Updated range of deltas in {original_name}: {updated_delta}')
        print(f'Updated list of modes in {original_name}: {updated_n}')
         

def merge_files(original_name, extension_name, option, modes, deltas, is_fixed_width, mishka):
    copy_original_file(original_name, extension_name, option)
    h5_manipulation.decompress_gz(extension_name)
    merge(original_name, extension_name, option, modes, deltas, is_fixed_width, mishka)
    h5_manipulation.removedoth5(extension_name)
    h5_manipulation.compress_to_gz(original_name)




if __name__ == '__main__':
    original_name, extension_name, option, modes, deltas, is_fixed_width, mishka = argument_parser()
    merge_files(original_name, extension_name, option, modes, deltas, is_fixed_width, mishka)