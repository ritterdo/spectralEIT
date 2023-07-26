## String Manipulation
#
# Author: Dominik Ritter
# Last Edit: 07.02.2022
#
# Discription:  format_float_to_scale transforms a number (int or float) into
#               into a string with scientific notation in magnitudes of three.
#               If custom_precision is not set than it will return all digits
#               until there not zero


import numpy as np


# Function to get a string in scientific notation back with a set magnitude
# and a set precision, default precision is 0
def format_float_to_scientific(number, magnitude, precision: int=0):
    try:
        float(number)
    except ValueError:
        return number
    if precision < 0 :
        print('Precision is smaller 0!')
        return 0
    return "{n:.{pr}f}e{e:d}".format(n=number/magnitude, e=int("{:e}".format(magnitude).split("e")[1]),pr=precision)


# Function to get the "corresponting" magnitude in orders of three
# example:  1e2  -> 1e0
#           1e5  -> 1e3
#           1e-4 -> 1e-6
def get_magnitude(exp):
    if type(exp) is not int:
        print('exponential is not an integer!')
        return 0
    if exp < 0:
        exp = int( (np.abs(exp)-1)/3 + 1 ) * 3
        exp *= -1
    elif exp > 0:
        exp = int( exp/3 ) * 3
    return exp


# Function to automatically determine the corresponding magnitude and manipulate
# the digits to not change the number itself
# example:  12345 -> 1.2345e3, without a custom_precision
#           12345 -> 1.23e3, with a custom_precision of 2

def format_float_to_scale(number_list, custom_precision: int=5, plain: bool=False):
    if type(number_list) not in [np.ndarray,np.array,list]:
        return _format_float_to_scale(number_list, custom_precision, plain)
    tmp_list = []
    for number in number_list:
        tmp_list.append(_format_float_to_scale(number, custom_precision, plain))
    return ", ".join(tmp_list)

def _format_float_to_scale(number, custom_precision: int=5, plain: bool=False):
    if type(number) == str:
        return number

    try:
        float(number)
    except ValueError:
        return number
    if '.' in str(number):
        nLen = len(str(number)) - 1
    else:
        nLen = len(str(number))
    _, exp  = np.format_float_scientific(number, precision=nLen).format(number).split("e")

    e = get_magnitude(int(exp))

    tmp_n, tmp_exp = format_float_to_scientific(number, float("1e{}".format(int(e))), nLen).split('e')
    tmp =str(float(tmp_n)).split('.')[1]


    pr = len(tmp) if tmp != '0' else 0
    if e == 0:
        return "{n:.{pr}f}".format(n=number,pr=pr if pr <= custom_precision else custom_precision)
    if (e == -3 and pr != 0) and plain:
        return "{n:.{pr}f}".format(n=number,pr=pr if pr <= custom_precision else custom_precision)
    return format_float_to_scientific(number, float("1e{}".format(int(e))), precision=pr if pr <= custom_precision else custom_precision)
