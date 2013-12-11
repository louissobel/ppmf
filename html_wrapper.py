"""
module with functions to wrap some text in html such that
the file, when opened in a browser, will supply needed javascript to:
 - get the password
 - decrypt it, display raw text contents (for now!)

also function to _unwrap_ an html, returning just the cipher text

Needs to handle HTML entities in the cipher and plain text
Maybe base64 encode the ciphertext?
"""
import re
import fileinput
from base64 import b64encode, b64decode
import json
import mimetypes

import jinja2

# TODO: this is a lil jank
HTML_TEMPLATE = jinja2.Template(open('cryptbox_template.html', 'r').read())

def wrap(cipherblock):
    """
    returns html string wrapping the ciphertext

    JSON object: {
        ciphertext: ciphertext,
        mimetype: type of file,
        keys: {
            key fingerprint : password encrypted with the public key
        }
    }
    """
    return HTML_TEMPLATE.render(ciphertext=b64encode(json.dumps(cipherblock)))

def unwrap(html_string):
    """
    gets the cipher text back out of this
    """
    match = re.search(r'\<pre id="ciphertext"\>(.*?)\</pre\>', html_string, re.DOTALL)
    if not match:
        raise ValueError("html_string %r does not match" % html_string)
    else:
        return json.loads(b64decode(match.group(1)))

if __name__ == "__main__":
    import sys

    source = ''.join([ line for line in fileinput.input(sys.argv[2:][0]) ])
    if sys.argv[1] == 'wrap':
        print wrap(source)
    elif sys.argv[1] == 'unwrap':
        print unwrap(source)
    else:
        raise ValueError
