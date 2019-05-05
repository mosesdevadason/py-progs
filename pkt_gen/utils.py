import re

def mac_str_to_int(addr):
    """
    Returns integer value for a given MAC address string.
    :param addr: MAC address in : seperated string format.
    :return: Integer value.
    """
    addr = addr.upper()
    re_mac_fmt = '^' + ':'.join(['([0-9A-F]{1,2})'] * 6) + '$'
    match_result = re.findall(re_mac_fmt, addr)

    words = list(match_result[0])
    int_val = None
    if len(words) == 6:
        int_val = int(''.join(['%.2x' % int(w, 16) for w in words]), 16)
    else:
        raise TypeError('%s is not in : separated MAC string format')
    return int_val

def __mac_int_to_words(int_val):
    """
    Returns six 8-bit words as a list for the given integer value.
    :param int_val: Integer value.
    :return: List of six 8-bit words.
    """
    max_int = 2 ** (6 * 8) - 1
    if not 0 <= int_val <= max_int:
        raise IndexError('Integer value out of bounds %r' % hex(int_val))

    words = []
    for _ in range (6):
        word = 0xff & int_val
        words.append(int(word))
        int_val = int_val >> 8

    return list(reversed(words))

def mac_int_to_str(int_val):
    """
    Returns MAC address in string format for the given integer.
    :param int_val: Integer value.
    :return: MAC address in string format.
    """
    words = __mac_int_to_words(int_val)
    return ':'.join(['%.2x' % w for w in words])
