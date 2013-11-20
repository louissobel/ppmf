"""
responsible for picking which strategy to use
"""
import sys

import using_applescript
import using_tkinter

def get_password(forwhat):
    p = sys.platform

    if p.startswith('linux'):
        return using_tkinter.get_password(forwhat)
    elif p.startswith('darwin'):
        return using_applescript.get_password(forwhat)
    else:
        raise NotImplementedError('Cannot get password on platform %s' % p)

if __name__ == "__main__":
    """
    Simple Check
    """
    print get_password('Testing')