import os
import subprocess
from europed_suite import useful_recurring_functions, h5_manipulation, hdf5_data
import matplotlib.pyplot as plt
from matplotlib import ticker
from jetlib.misc import ReadFile
import h5py
import gzip
import tempfile
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import glob
import re
import math
import scipy.interpolate
from collections import OrderedDict
import fcntl

def lock_file(file):
    fcntl.flock(file, fcntl.LOCK_EX)

def unlock_file(file):
    fcntl.flock(file, fcntl.LOCK_UN)

def get_x_parameter(filename, x_parameter="alpha_helena_max", q_ped_def="tepos-delta"):
    if x_parameter in ['peped','teped','neped','nesep_neped']:
        nrows = hdf5_data.get(filename, ['input','steps'])
        if nrows == None:
            nrows = len(hdf5_data.get(filename, ['scan']))
        res = np.zeros((nrows))
        for i in range(nrows):
            res[i] = None
            try:
                if x_parameter in ['peped','teped','neped']:
                    q = x_parameter[:2]
                    res[i] = pedestal_values.pedestal_value_all_definition(q,filename, profile=i, q_ped_def=q_ped_def)
                elif x_parameter == 'nesep_neped':
                    res[i] = pedestal_values.nesep_neped(filename, profile=i, q_ped_def=q_ped_def)
            except KeyError as e:
                print(f'KeyError: {e}')
            except ValueError as e:
                print(f'ValueError: {e}')
    else:
        res = hdf5_data.get_xparam(filename, x_parameter)
    return sorted(res)


def get_x_parameter_with_stability(filename, x_parameter="alpha_helena_max", q_ped_def="tepos-delta"):
    if x_parameter in ['peped','teped','neped','nesep_neped']:
        nrows = hdf5_data.get(filename, ['input','steps'])
        res = np.zeros((nrows))
        for i in range(nrows):
            res[i] = None
            try:
                temp = hdf5_data.get(filename, ['scan',str(i),'castor'])
                if temp is None:
                    continue

                if x_parameter in ['peped','teped','neped']:
                    q = x_parameter[:2]
                    res[i] = pedestal_values.pedestal_value_all_definition(q,filename, profile=i, q_ped_def=q_ped_def)
                elif x_parameter == 'nesep_neped':
                    res[i] = pedestal_values.nesep_neped(filename, profile=i, q_ped_def=q_ped_def)
            except KeyError as e:
                print(f'KeyError: {e}')
    else:
        res = hdf5_data.get_xparam_with_stability(filename, x_parameter)

    return sorted(res)

def interpolate_points(x_values,y_values, num_points=100):    
    # Linearly interpolate to get 100 points between the minimum and maximum x values
    x_values_valid = x_values
    y_values_valid = y_values
    interpolated_x = np.linspace(min(x_values), max(x_values), num_points)
    interpolated_y = np.interp(interpolated_x, x_values_valid, y_values_valid)
    return interpolated_x,interpolated_y


def interpolate_points_wborders(main_x_values, x_values, y_values, num_points=300):    
    # Linearly interpolate to get 100 points between the minimum and maximum x values
    interpolated_main_x = np.linspace(min(main_x_values), max(main_x_values), num_points)
    are_in_temp_x = [x>= min(x_values) and x <= max(x_values) for x in interpolated_main_x]
    # (interpolated_main_x <= max(x_values)) & (interpolated_main_x >= min(x_values))
    num_point_in_borders = np.sum(are_in_temp_x)
    res_y = np.full(num_points, None)
    interpolated_x = np.linspace(min(x_values), max(x_values), num_point_in_borders)
    interpolated_y = np.interp(interpolated_x, x_values, y_values)
    res_y[are_in_temp_x] = interpolated_y      
    return res_y


def list_n_from_dict(dict_gammas):
    list_n = []
    for delta in list(dict_gammas.keys()):
        list_n += list(dict_gammas[delta].keys())
    return sorted(set(list_n))

# def get_critical_profiles(europed_name, crit, crit_value, psis, y_parameter, exclud_mode):
#     deltas = get_x_parameter(europed_name, 'delta')
#     dict_gamma = get_filtered_dict(europed_name, crit, exclud_modes=exclud_mode)
#     delta_crit = find_critical(deltas, deltas, dict_gamma, crit_value)
#     delta_below = max([d for d in deltas if d < delta_crit])
#     delta_above = max([d for d in deltas if d > delta_crit])

def reverse_nested_dict(d):
    reversed_dict = {}
    for first_level_key, second_level_dict in d.items():
        for second_level_key, value in second_level_dict.items():
            if second_level_key not in reversed_dict:
                reversed_dict[second_level_key] = {}
            reversed_dict[second_level_key][first_level_key] = value
    res = OrderedDict(sorted(reversed_dict.items()))
    return res

def give_envelop(dict_gammas, delta_input, x_parameter=None):
    nb_points = 1000
    dict_gammas_r = reverse_nested_dict(dict_gammas)
    all_deltas = delta_input
    nb_n = len(list_n_from_dict(dict_gammas))
    list_interpolator = []
    for i,(n,inner_dict) in enumerate(dict_gammas_r.items()):
        temp_delta = list(inner_dict.keys())
        temp_gamma = list(inner_dict.values())
        # temp_delta,temp_gamma = sorted(list(temp_delta)),sorted(list(temp_gamma))
        temp_x = give_matching_x_with_deltas(all_deltas, x_parameter, temp_delta)
        interpolator = scipy.interpolate.interp1d(temp_x, temp_gamma, bounds_error=False, fill_value=None)
        list_interpolator.append(interpolator)
    x_envelope = np.linspace(np.nanmin(x_parameter), np.nanmax(x_parameter), nb_points)
    y_envelope = np.zeros((nb_points))
    for i,x in enumerate(x_envelope):
        interpolated_y = [interp(x) for interp in list_interpolator]
        if np.all(interpolated_y == None):
            y_envelope[i] = None
        else:
            max_y = np.nanmax(interpolated_y)
            if np.isnan(max_y):
                max_y = None
            y_envelope[i] = max_y

    return(x_envelope,y_envelope)


def give_matching_x_with_deltas(delta_input, x_input, delta_to_plot):

    delta_input = np.array(delta_input)
    x_input = np.array(x_input)

    non_nan_mask = ~np.isnan(delta_input)
    sorted_non_nan = np.sort(delta_input[non_nan_mask])
    delta_input = np.concatenate([sorted_non_nan, delta_input[~non_nan_mask]])

    non_nan_mask = ~np.isnan(x_input)
    sorted_non_nan = np.sort(x_input[non_nan_mask])
    x_input = np.concatenate([sorted_non_nan, x_input[~non_nan_mask]])

    delta_input = [round(d,5) for d in delta_input]
    delta_to_plot = [round(d,5) for d in delta_to_plot]
    mask = [np.any(np.abs(delta_to_plot-d)<1e-4) for d in delta_input]
    x_input = np.array(x_input)
    x_to_plot = x_input[mask]


    return x_to_plot


def remove_wrong_slope(dict_gamma):
    dict_gamma_r = reverse_nested_dict(dict_gamma)
    for n in dict_gamma_r.keys():
        dict_gamma_mode = dict_gamma_r[n]
        list_items = list(dict_gamma_mode.items())
        list_items = sorted(list_items, key=lambda x: x[0])
        for i in range(len(list_items)-1):
            if list_items[i+1][1] < list_items[i][1]:
                del dict_gamma_mode[list_items[i][0]]
    dict_gamma = reverse_nested_dict(dict_gamma_r)
    return dict_gamma



def get_gammas(filename, crit="alfven", fixed_width=False):
    zipped = h5_manipulation.decompress_gz(filename)
    # Open the temporary file with h5py
    with h5py.File(filename + '.h5', 'r') as hdf5_file:
        # lock_file(hdf5_file)
        # try:
        group_scan = hdf5_file['scan']
        list_profile = list(hdf5_file['scan'].keys())
        # n = hdf5_file['input']['steps'][0]
        # list_profile = range(n)

        stability_code = ''
        i = 0
        while stability_code == '':
            if 'castor' in list(hdf5_file['scan'][str(list_profile[i])].keys()):
                stability_code = 'castor'
            elif 'mishka' in list(hdf5_file['scan'][str(list_profile[i])].keys()):
                stability_code = 'mishka'
            i += 1
            if i == len(list_profile):
                return None 

        # stability_code = 'castor' if 'castor' in list(hdf5_file['scan'][list_profile[0]].keys()) else 'mishka'

        list_mode = []

        for i in list_profile:
            try:
                list_mode += list(hdf5_file['scan'][str(i)][stability_code].keys())
            except KeyError:
                pass

        list_modes = list(set(list_mode))
        list_modes = [int(n) for n in list_modes]

        # list_modes = [int(i) for i in hdf5_file['input']['n'][0].decode('utf-8').split(',')]
        list_modes_output = []

        dict_results = {}
        dict_res = {}

        # temp = str(hdf5_file['input']['stability_code'][0])
        # stability_code = re.findall(r"'(.*?)'", temp)[0]
        #   (f"{original_filename:<36}{stability_code}")

        for profile in list_profile:
            try:
                group_prof = group_scan[str(profile)][stability_code] 
                if not fixed_width: 
                    delta = round(float(group_scan[str(profile)]['delta'][0]),5)
                else:
                    delta = round(float(group_scan[str(profile)]['betaped'][0]),5)
                dict_results[delta] = {}
                for i_n, n in enumerate(list_modes):
                    try:
                        group_mode = group_prof[str(n)]

                        if crit == "alfven":
                            temp_res = group_mode['gamma'][0]
                        elif crit == "diamag":
                            temp_res = group_mode['gamma_diam'][0]
                        elif crit == "omega":
                            temp_res = group_mode['omega'][0]
                        dict_results[delta][n] = temp_res
                    except KeyError:
                        continue
                dict_res[delta] = OrderedDict(sorted(dict_results[delta].items()))
            except KeyError:
                pass
                # print(f"{filename:>40} No profile {profile}")

        # except KeyError:
        #     print(f"{filename:>40} Unable to open 'scan'")
        #     return None
        # unlock_file(hdf5_file)

    if zipped:
        h5_manipulation.removedoth5(filename)

    return dict_res

def get_runid(europed_run):
    filepath = ""
    filepath = f"{os.environ['EUROPED_DIR']}output/{europed_run}"
    with ReadFile(filepath) as f:
        line = f.readline()
        while 'run id:' not in line:
            line=f.readline()
        lines = line.split(': ')
        runid = lines[1][:-1]
    return runid

def filter_dict(dict_gamma, interesting_modes=None, exclud_mode=None):
    if interesting_modes is None:
        full_n = list_n_from_dict(dict_gamma)
        temp = [n for n in full_n if not n in exclud_mode]
        interesting_modes = temp
    dict_gamma_r = reverse_nested_dict(dict_gamma)
    filtered_dict = {key: dict_gamma_r[key] for key in dict_gamma_r.keys() if key in interesting_modes}
    filtered_dict_r = reverse_nested_dict(filtered_dict)
    dict_res = {}
    for d in filtered_dict_r.keys():
        dict_res[d] = OrderedDict(sorted(filtered_dict_r[d].items()))
    return dict_res

def get_filtered_dict(europed_name, crit, consid_modes=None, exclud_modes=None, fixed_width=False):
    dict_gamma = get_gammas(europed_name, crit, fixed_width)
    available_modes = list_n_from_dict(dict_gamma)
    if consid_modes:
        interesting_modes = [m for m in available_modes if m in consid_modes]
    elif exclud_modes:
        interesting_modes = [m for m in available_modes if m not in exclud_modes]
    else:
        return dict_gamma
    dict_gamma = filter_dict(dict_gamma, interesting_modes)
    dict_gamma = OrderedDict(sorted(dict_gamma.items()))
    return dict_gamma

def give_maximal_n(dict_gamma):
    results = []
    for delta, subdict in dict_gamma.items():
        gamma_max = 0
        n_max = 0
        for n,gamma in subdict.items():
            if gamma > gamma_max:
                n_max = n
                gamma_max = gamma
        results.append((delta, gamma_max, n_max))
    return results

def has_unstable(dict_gamma, crit_value):
    for delta,subdict in dict_gamma.items():
        for n,gamma in subdict.items():
            if gamma > crit_value:
                return True
    return False

def has_unstable_for_given_n(subdict, crit_value):
    for n,gamma in subdict.items():
        if gamma > crit_value:
            return True
    return False

def has_below_threshold(subdict, crit_value):
    for n,gamma in subdict.items():
        if gamma < crit_value:
            return True
    return False

def filter_gamma_before_max(list_gamma, list_x):
    idx = np.argmax(list_gamma)
    gamma = list_gamma[:idx+1]
    x = list_x[:idx+1]
    return gamma,x

def critical_value(list_gamma, crit_value, list_x_parameter):
    sorted_indices = np.argsort(list_x_parameter)
    list_gamma = np.array(list_gamma)
    list_x_parameter = np.array(list_x_parameter)
    list_gamma = list_gamma[sorted_indices]
    list_x_parameter = list_x_parameter[sorted_indices]
    if list_gamma[0] > crit_value:
        return list_x_parameter[0]
    list_gamma, list_x_parameter = filter_gamma_before_max(list_gamma, list_x_parameter)
    list_gamma = np.array(list_gamma)
    list_x_parameter = np.array(list_x_parameter)
    list_gamma_diff = list_gamma[1:] - list_gamma[:-1]

    temp = np.where(list_gamma_diff<0)[0]

    if temp != []:
        index_of_max = np.min(temp)
        value_of_max = list_gamma[index_of_max]

        test1 = np.where(list_gamma<value_of_max)
        list_indexes = range(len(list_gamma))
        test2 = np.where(list_indexes>index_of_max)

        index_to_remove = np.intersect1d(test1, test2)
        indexes_to_keep = [i for i in list_indexes if not i in index_to_remove]
        list_gamma = list_gamma[indexes_to_keep]
        list_x_parameter = list_x_parameter[indexes_to_keep]
    interpolator = scipy.interpolate.interp1d(list_gamma, list_x_parameter, bounds_error=True)
    try:
        x_crit = interpolator(crit_value)
    except ValueError:
        x_crit = min(list_x_parameter)
    return x_crit

def get_critical_for_given_n(dict_gamma, delta_input, x_input, crit_value, n):
    dict_gamma_r = reverse_nested_dict(dict_gamma)
    subdict = dict_gamma_r[n]
    sorted_dict = OrderedDict(sorted(subdict.items()))

    list_gamma = list(sorted_dict.values())
    delta_to_plot = list(sorted_dict.keys())
    x_to_plot = give_matching_x_with_deltas(sorted(delta_input), sorted(x_input), delta_to_plot)
    # x_to_plot = x_input

    if has_unstable_for_given_n(subdict, crit_value):
        if not has_below_threshold(subdict, crit_value):
            return -np.inf, np.nanmin(x_to_plot)
        else:
            x_crit = critical_value(list_gamma, crit_value, x_to_plot)
            return x_crit, x_crit
    else:
        return None, None


def find_critical(x_input, delta_input, dict_gamma, crit_value):
    x_input = sorted(x_input)
    delta_input = sorted(delta_input)
    list_n = list_n_from_dict(dict_gamma)
    dict_crit_values = {}

    for n in list_n:
        res_crit = get_critical_for_given_n(dict_gamma, delta_input, x_input, crit_value, n)


        if not (res_crit[0] is None):
            dict_crit_values[n] = res_crit

    if np.all(list(dict_crit_values) is None):
        return False, None, -1
    
    list_pairs = list(dict_crit_values.items())
    list_pairs = [p for p in list_pairs if not p[1][1] is None and not np.isnan(p[1][1])]


    try:
        min_pair = min(list_pairs, key=lambda item: item[1][1])
    except ValueError:
        return False, None, -1
    crit_n = min_pair[0]
    crit_x = min_pair[1][0]

    if crit_x == np.nanmin(x_input):        
        return True, crit_x, -1
    elif crit_x == -np.inf:
        return True, np.nanmin(x_input), -1
    else:
        return True, crit_x, crit_n



def critical_value_europed_name(europed_name, crit, crit_value, x_param, q_ped_def='tepos-delta', list_consid_mode=None):
    if x_param == 'alpha':
        x_param = 'alpha_helena_max'
    elif x_param == 'frac':
        crit_value = pedestal_values.nesep_neped(europed_name, crit=crit, crit_value=crit_value, q_ped_def=q_ped_def, list_consid_mode=list_consid_mode)
        return crit_value
    elif x_param in ['pe','ne','te','peped','teped','neped']:
        crit_value = pedestal_values.pedestal_value_all_definition(x_param[:2], europed_name, crit=crit, crit_value=crit_value, q_ped_def=q_ped_def, list_consid_mode=list_consid_mode)
        return crit_value
    dict_gamma = get_filtered_dict(europed_name, crit, consid_modes=list_consid_mode)
    deltas = hdf5_data.get_xparam(europed_name, 'delta')
    x_parameter = hdf5_data.get_xparam(europed_name, x_param)
    bim, bam, bum = find_critical(x_parameter, deltas, dict_gamma, crit_value)
    return bam

def critical_value_europed_name_withoutlowerpoint(europed_name, crit, crit_value, x_param, q_ped_def='tepos-delta', list_consid_mode=None):
    if x_param == 'alpha':
        x_param = 'alpha_helena_max'
    elif x_param == 'frac':
        crit_value = pedestal_values.nesep_neped(europed_name, crit=crit, crit_value=crit_value, q_ped_def=q_ped_def, list_consid_mode=list_consid_mode)
        return crit_value
    elif x_param in ['pe','ne','te','peped','teped','neped']:
        crit_value = pedestal_values.pedestal_value_all_definition(x_param[:2], europed_name, crit=crit, crit_value=crit_value, q_ped_def=q_ped_def, list_consid_mode=list_consid_mode)
        return crit_value
    dict_gamma = get_filtered_dict(europed_name, crit, consid_modes=list_consid_mode)
    deltas = hdf5_data.get_xparam(europed_name, 'delta')
    x_parameter = hdf5_data.get_xparam(europed_name, x_param)
    bim, bam, bum = find_critical(x_parameter, deltas, dict_gamma, crit_value)
    if bum == -1:
        return None
    return bam


