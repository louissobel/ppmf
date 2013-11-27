"""
parses open flags
"""
import os

# Flag to extract access bits - not in os
# so this is possibly jank jank
O_ACCESS = 3

class OpenFlags(object):

    FIELDS = (
        'read',
        'write',
    )

    @classmethod
    def from_int(cls, flags):
        access = flags & O_ACCESS

        vals = {
            'read' : False,
            'write' : False,
        }

        if access == os.O_RDONLY:
            vals['read'] = True
        elif access == os.O_WRONLY:
            vals['write'] = True
        elif access == os.O_RDWR:
            vals['read'] = True
            vals['write'] = True

        return cls(**vals)

    def __init__(self, **kwargs):
        for f in self.FIELDS:
            setattr(self, f, kwargs.get(f, False))

    def __str__(self):
        read = 'r' if self.read else ''
        write = 'w' if self.write else ''
        return (read + write) or '-'

def parse(flags):
    return OpenFlags.from_int(flags)
