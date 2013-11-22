"""
pops up applescript prompt to get password
"""
from PyASDialog import ASDialog


def get_password(forwhat):
    myDialog = ASDialog(
        title="Cryptbox Password Required",
        text="Password required to decrypt %s" % forwhat,
        defaultAnswer="",
        hiddenAnswer = True,
        icon='0',
    )
    res = myDialog.result()
    if 'canceled' in res:
        return None
    else:
        return res['text returned']
