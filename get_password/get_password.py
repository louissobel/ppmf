"""
responsible for picking which strategy to use
"""
import sys
import os

import using_applescript
import using_tkinter
import using_test

def get_password(forwhat):
    p = sys.platform

    # testing?
    if os.environ.get('TEST_CRYPTBOXFS') is not None:
        return using_test.get_password(forwhat)

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