from fullcontrol import ManualGcode

def set_linear_advance(k_value: float):
    return ManualGcode(text='M900 K'+str(k_value)+'; set LA')