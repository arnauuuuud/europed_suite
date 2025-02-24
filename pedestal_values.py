import os
from europed_suite import useful_recurring_functions, europed_analysis, h5_manipulation, hdf5_data
import matplotlib.pyplot as plt
import h5py
import gzip
import tempfile
import numpy as np
import scipy
import glob
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d,interp2d

def mtanh_offset(r, ppos, delta, h, s, offset):
    x = 2*(ppos-r)/delta
    res = h/2*(((1+s*x)*np.exp(x)-np.exp(-x))/(np.exp(x)+np.exp(-x)) + 1) + offset
    return res

def fit_mtanh(psis, ne_profile):
    params, covariance = curve_fit(mtanh_offset, psis, ne_profile, p0=[0.95, 0.05, 4.5, 1, 0.01])
    return params

   
def profile_pars(filename, profile):
    h5_manipulation.decompress_gz(filename)
    with h5py.File(f'{filename}.h5', 'r') as hdf5_file:
        ne_pars = tuple(hdf5_file['scan'][str(profile)]['ne_parameters'])
        te_pars = tuple(hdf5_file['scan'][str(profile)]['te_parameters'])   
    h5_manipulation.removedoth5(filename)
    return(te_pars, ne_pars)

def ne_pars(filename, profile):
    h5_manipulation.decompress_gz(filename)
    with h5py.File(f'{filename}.h5', 'r') as hdf5_file:
        ne_pars = tuple(hdf5_file['scan'][str(profile)]['ne_parameters'])
    h5_manipulation.removedoth5(filename)
    return(ne_pars)

def te_pars(filename, profile):
    h5_manipulation.decompress_gz(filename)
    with h5py.File(f'{filename}.h5', 'r') as hdf5_file:
        te_pars = tuple(hdf5_file['scan'][str(profile)]['te_parameters'])
    h5_manipulation.removedoth5(filename)
    return(te_pars)


def eped_profile(pars, psi):
    """
    Takes profile parameters from europed to return profile value at psi
    Arguments:
        pars : iterable
            iterable of length 8 containing the profile parameters
        psi : float/iterable
            if iterable returns numpy array with profile values at psi
            else returns profile value at psi
    """
    def core_profile(a1, pedestal, alpha1, alpha2, x):
        if psi > pedestal:
            return 0.0
        else:
            return a1*(1-(x/pedestal)**alpha1)**alpha2

    def pedestal_profile(sep, a0, pos, delta, x):
        return sep+a0*(np.tanh(2*(1-pos)/delta)-np.tanh(2*(x-pos)/delta))
    
    (a0, sep, a1, pos, delta, pedestal, alpha1, alpha2) = pars
    
    if isinstance(psi, float) or isinstance(psi, int):
        ped = pedestal_profile(sep, a0, pos, delta, psi)
        if (psi > pedestal):
            return ped
        else:
            core = core_profile(a1, pedestal, alpha1, alpha2, psi)
            return ped + core
    else:
        prof = np.empty(len(psi))
        for i in range(len(psi)):
            prof[i] = eped_profile(pars, psi[i])
        return prof

def create_standard_profiles(europed_name, psis, profile):
    te_pars, ne_pars = profile_pars(europed_name, profile)
    te_profile = np.zeros(len(psis))
    ne_profile = np.zeros(len(psis))
    for i,psi in enumerate(psis):
        te_profile[i] = eped_profile(te_pars, psi)
        ne_profile[i] = eped_profile(ne_pars, psi)
    return te_profile, ne_profile

def get_critical_pars(europed_name, crit='alfven', crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    profile_below, profile_above, ratio = critical_profile_number(europed_name, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    te_pars_below, ne_pars_below = profile_pars(europed_name, profile=profile_below)
    te_pars_above, ne_pars_above = profile_pars(europed_name, profile=profile_above)

    te_pars_below = np.array(te_pars_below)
    ne_pars_below = np.array(ne_pars_below)
    te_pars_above = np.array(te_pars_above)
    ne_pars_above = np.array(ne_pars_above)

    te_pars_crit = te_pars_below*(1-ratio) + te_pars_above*ratio
    ne_pars_crit = ne_pars_below*(1-ratio) + ne_pars_above*ratio
    return te_pars_crit, ne_pars_crit

def create_critical_profiles(europed_name, psis, crit='alfven', crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    profile_below, profile_above, ratio = critical_profile_number(europed_name, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    te_below, ne_below = create_standard_profiles(europed_name, psis, profile=profile_below)
    te_above, ne_above = create_standard_profiles(europed_name, psis, profile=profile_above)
    interp_ne = interp2d(psis,[0,1],[ne_below, ne_above])
    interp_te = interp2d(psis,[0,1],[te_below, te_above])
    ne_profile_crit = interp_ne(psis,ratio)
    te_profile_crit = interp_te(psis,ratio)
    return te_profile_crit, ne_profile_crit


def critical_profile_number(europed_name, crit='alfven', crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    if not fixed_width:
        deltas = hdf5_data.get_xparam(europed_name, 'delta')
    else:
        deltas = hdf5_data.get_xparam(europed_name, 'betaped')
    dict_gammas = europed_analysis.get_filtered_dict(europed_name, crit, list_consid_mode, exclud_mode, fixed_width)
    if crit =='diamag':
        dict_gammas = europed_analysis.remove_wrong_slope(dict_gammas)
    has_unstable, delta_crit, mode = europed_analysis.find_critical(deltas, deltas, dict_gammas, crit_value)
    try:
        delta_below = np.max([d for d in deltas if d <= delta_crit])
    except ValueError:
        return None, None, None
    delta_above = np.min([d for d in deltas if d > delta_crit])
    h5_manipulation.decompress_gz(europed_name)
    with h5py.File(europed_name + '.h5', 'r') as h5file:
        try:
            if not fixed_width:
                profile_below = h5_manipulation.find_profile_with_delta_file(h5file,delta_below)
                profile_above = h5_manipulation.find_profile_with_delta_file(h5file,delta_above)
            else:
                profile_below = h5_manipulation.find_profile_with_betaped_file(h5file,delta_below)
                profile_above = h5_manipulation.find_profile_with_betaped_file(h5file,delta_above)
        except useful_recurring_functions.CustomError:
            return None, None, None
    h5_manipulation.removedoth5(europed_name)

    proportionality_ratio = (delta_crit-delta_below)/(delta_above-delta_below)
    return profile_below, profile_above, proportionality_ratio

def get_pars(europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    if (profile is None) and (not crit is None):
        return get_critical_pars(europed_name, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    elif (not profile is None) and (crit is None):
        return profile_pars(europed_name, profile)


def create_profiles(europed_name, psis, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    if (profile is None) and (not crit is None):
        return create_critical_profiles(europed_name, psis, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    elif (not profile is None) and (crit is None):
        return create_standard_profiles(europed_name, psis, profile)
    else:
        print('Error in create_profiles from pedestal_values.py, choose either profile or crit')
        return None, None

def create_pressure_profile(europed_name, psis, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    te_p, ne_p = create_profiles(europed_name, psis, profile=profile, crit=crit, crit_value=crit_value, exclud_mode=exclud_mode, list_consid_mode=list_consid_mode, fixed_width=fixed_width)
    te_p = np.array(te_p)
    ne_p = np.array(ne_p)
    temp = ne_p * te_p
    pe_profile = 1.6*temp
    return pe_profile


def get_fit_width(europed_name, q, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    psis = np.linspace(0.8,1,200)
    if q == 'ne':
        trash, profile = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    elif q == 'te':
        profile, trash = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    elif q == 'pe':
        profile = create_pressure_profile(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)

    params = fit_mtanh(psis, profile)
    return params[1]

def get_fit_rs(europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    psis = np.linspace(0.8,1,200)

    te_profile, ne_profile = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    params_ne = fit_mtanh(psis, ne_profile)
    params_te = fit_mtanh(psis, te_profile)
    return params_ne[0]-params_te[0]

def get_rs(europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False):
    te_pars, ne_pars = get_pars(europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    return ne_pars[3]-te_pars[3 ]


def standard_te_pos(europed_name, profile):
    te_pars, ne_pars = profile_pars(europed_name, profile)
    (a0, sep, a1, pos, delta, pedestal, alpha1, alpha2) = te_pars
    teped = 2*a0 + sep + a0*(np.tanh(2*(1-pos)/delta)-1)
    return pos-delta/2

def critical_te_pos(europed_name, crit='alfven', crit_value=0.05, exclud_mode = [30,40,50], list_consid_mode = None, fixed_width = False):
    p1, p2, ratio = critical_profile_number(europed_name, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    pos1 = standard_te_pos(europed_name, profile=p1)
    pos2 = standard_te_pos(europed_name, profile=p2)
    pos = pos1+ (pos2-pos1)*ratio
    return pos

def te_pos(europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width = False):
    if (profile is None) and (not crit is None):
        return critical_te_pos(europed_name, crit, crit_value, exclud_mode, list_consid_mode, fixed_width)
    elif (not profile is None) and (crit is None):
        return standard_te_pos(europed_name, profile)
    else:
        print('Error in te_pos from pedestal_values.py, choose either profile or crit')
        return None


def pepos_and_delta(europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None):
    psis = np.linspace(0.8,1.2,200)
    fw = europed_name.startswith('fw')
    pe_profile = create_pressure_profile(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fixed_width=fw)
    pe_pars = fit_mtanh(psis, pe_profile)
    pos = pe_pars[0]
    delta = pe_pars[1]
    return pos, delta

def te_pos_minus_hdelta(europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None):
    psis = np.linspace(0.8,1.2,200)
    fw = europed_name.startswith('fw')
    te_profile, ne_profile = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fixed_width=fw)
    te_pars = fit_mtanh(psis, te_profile)
    pos = te_pars[0]
    delta = te_pars[1]
    return pos-delta/2


def pedestal_value(q, europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None):
    psis = np.linspace(0.85,1,200)
    fw = europed_name.startswith('fw')
    if q == 'te':
        qprofile = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fw)[0]
    elif q == 'ne':
        qprofile = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fw)[1]
    elif q == 'pe':
        qprofile = create_pressure_profile(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fw)
    else:
        print('Choose q in pedestal_value from "ne","te","pe"')
    pos = te_pos_minus_hdelta(europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode)
    # pos = te_pos(europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode)
    interpolator = scipy.interpolate.interp1d(psis,qprofile)
    try:
        q_ped = interpolator(pos)
    except ValueError:
        return None
    return q_ped


def nesep(europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None):
    psis = np.linspace(0.85,1.2, 100)
    fw = europed_name.startswith('fw')
    # europed_name, psis, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, fixed_width=False
    te_profile, ne_profile = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode, fw)

    interp_te_psi = interp1d(te_profile, psis)
    psi_01 = interp_te_psi(0.1)
    interp_psi_ne = interp1d(psis, ne_profile)
    nesep = interp_psi_ne(psi_01)
    return nesep



def nesep_neped(europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, q_ped_def='tepos-delta'):
    ne_sep = nesep(europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode)
    ne_ped = pedestal_value_all_definition('ne', europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode, q_ped_def)
    try:
        frac = ne_sep/ne_ped
    except TypeError:
        return None
    return(frac)

### Pedestal value all definitions
def pedestal_value_all_definition(q, europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, q_ped_def='tepos-delta'):
    q = q[:2]
    if q_ped_def == 'tepos-delta':
        return pedestal_value(q, europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode)

    elif q_ped_def == 'product':
        return pedestal_product(q, europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode)

    elif q_ped_def == 'fixedposition':
        position = 0.95
        return pedestal_fixedposition(q, europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode, position)

    elif q_ped_def == 'positionTeped':
        return pedestal_positionTeped(q, europed_name, profile, crit, crit_value, exclud_mode, list_consid_mode)


### Pedestal values from hdf5
def pedestal_product(q, europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None):
    if profile is not None and crit is None:
        qped = profile_pedestal_product(q, europed_name, profile)
    elif crit is not None and profile is None:
        qped = critical_pedestal_product(q, europed_name, crit, crit_value, exclud_mode, list_consid_mode)
    return qped


def profile_pedestal_product(q, europed_name, profile=None):
    try:
        neped = hdf5_data.get(europed_name, ['scan', str(profile), 'neped'])
        teped = hdf5_data.get(europed_name, ['scan', str(profile), 'teped'])
    except TypeError:
        return None
    if q == 'pe':
        peped = 1.6 * neped * teped
        return peped
    elif q == 'te':
        return teped
    elif q == 'ne':
        return neped
        
def critical_pedestal_product(q, europed_name, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None):
    profile_below, profile_above, ratio = critical_profile_number(europed_name, crit, crit_value, exclud_mode, list_consid_mode)
    
    neped_below = hdf5_data.get(europed_name, ['scan', profile_below, 'neped'])
    neped_above = hdf5_data.get(europed_name, ['scan', profile_above, 'neped'])
    teped_below = hdf5_data.get(europed_name, ['scan', profile_below, 'teped'])
    teped_above = hdf5_data.get(europed_name, ['scan', profile_above, 'teped'])

    neped = ratio*neped_below + (1-ratio)*neped_above
    teped = ratio*teped_below + (1-ratio)*teped_above
    peped = 1.6*neped*teped

    if q == 'pe':
        return peped
    elif q == 'te':
        return teped
    elif q == 'ne':
        return neped


### Fixed position pedestal values
def pedestal_fixedposition(q, europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None, position=0.95):
    psis = np.linspace(0, 1, 100)
    profileq = 0 
    if q == 'pe':
        profileq = create_pressure_profile(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode)
    elif q in ['te','ne']:
        te, ne = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode)
        profileq = te if q == 'te' else ne
    interpolator = scipy.interpolate.interp1d(psis, profileq)
    qped = interpolator(position)
    return(qped)

### Pedestal values for Teped position
def pedestal_positionTeped(q, europed_name, profile=None, crit=None, crit_value=0.03, exclud_mode = None, list_consid_mode = None):
    if profile is not None and crit is None:
        teped = hdf5_data.get(europed_name, ['scan', str(profile), 'teped'])
    elif profile is None and crit is not None:
        profile_below, profile_above, ratio = critical_profile_number(europed_name, crit, crit_value, exclud_mode, list_consid_mode)
        teped_below = hdf5_data.get(europed_name, ['scan', str(profile_below), 'teped'])
        teped_above = hdf5_data.get(europed_name, ['scan', str(profile_above), 'teped'])
        teped = ratio*teped_below + (1-ratio)*teped_above
    
    if q == 'te':
        return(teped)
    elif q in ['ne','pe'] :
        psis = np.linspace(0, 1, 100)
        te, ne = create_profiles(europed_name, psis, profile, crit, crit_value, exclud_mode, list_consid_mode)
        profileq = ne if q == 'ne' else 1.6*ne*te
        interpolator_tepsi = scipy.interpolate.interp1d(te, psis)
        psi_Teped = interpolator_tepsi(teped)
        interpolator_psiq = scipy.interpolate.interp1d(psis, profileq)
        qped = interpolator_psiq(psi_Teped)
        return(qped)

    