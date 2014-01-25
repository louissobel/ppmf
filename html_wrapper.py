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
import json
import mimetypes

import jinja2

import file_content
import encryption.util


class HTMLWrapper(object):
    """
    wraps and unwraps html
    """
    TEMPLATE_DIR = 'templates'

    def __init__(self, linelength=80):
        """
        optional linelength argument, controls width of ciphertext in html
        """
        self.linelength = linelength

        self.template_env = jinja2.Environment(loader=jinja2.PackageLoader(__name__, self.TEMPLATE_DIR))
        self.template_env.filters['linewrap'] = self.split_into_lines

    def wrap(self, encrypted_content):
        """
        returns html string wrapping the ciphertext
        """
        # Type check for sanity.
        required_klass = file_content.EncryptedContent
        if not isinstance(encrypted_content, required_klass):
            raise TypeError('Argument to wrap must be instance of %s' % str(required_klass))

        return self.template_env.get_template('cryptbox_template.html').render(ciphertext=encrypted_content.b64ciphertext)

    def split_into_lines(self, text):
        if self.linelength is None:
            return text
        else:
            return '\n'.join(text[i:i+self.linelength] for i in range(0, len(text), self.linelength))

    def unwrap(self, html_string):
        """
        gets the cipher text back out of this
        """
        match = re.search(r'\<pre id="ciphertext"\>(.*?)\</pre\>', html_string, re.DOTALL)
        if not match:
            raise ValueError("html_string %r does not match" % html_string)
        else:
            b64ciphertext = match.group(1)
            encrypted = file_content.EncryptedContent(b64ciphertext)
            return encrypted
