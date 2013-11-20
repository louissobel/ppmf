"""
spawns the subprocess

interprets the result
"""
import subprocess
import tkinter_subprocess

def get_password(forwhat):
    """
    spawns the tkinter subprocess
    """
    path = tkinter_subprocess.__file__

    try:
        return subprocess.check_output([
            'python',
            path,
            forwhat,
        ])
    except subprocess.CalledProcessError as e:
        if e.returncode == tkinter_subprocess.CANCEL_RETURN_CODE:
            # fine.
            return None
        else:
            raise
