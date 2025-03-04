import numpy as np

def parse_modes(mode_str):
    return mode_str.split(',')

def parse_list_modes(mode_str):
    temp = mode_str.split(':')
    res = [m.split(',') for m in temp]
    return res

def parse_delta(str):
    if ',' in str:
        return [float(delta) for delta in str.split(',')]
    elif '-' in str:
        delta_min = round(float(str.split('-')[0]),5)
        delta_max = round(float(str.split('-')[1]),5)
        step_size = 0.0005
        deltas = np.arange(delta_min, delta_max + step_size, step_size)
        return deltas
    else:
        return [float(str)]
    
def parse_betapped(str):
    if ',' in str:
        return [float(delta) for delta in str.split(',')]
    elif '-' in str:
        delta_min = round(float(str.split('-')[0]),5)
        delta_max = round(float(str.split('-')[1]),5)
        step_size = 0.25
        deltas = np.arange(delta_min, delta_max + step_size, step_size)
        return deltas
    else:
        return [float(str)]

class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message) 