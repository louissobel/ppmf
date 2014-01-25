"""
Main interface to encryption
"""
import sys
import mimetypes

import file_content
import html_wrapper

DEFAULT_MIMETYPE = 'application/octet-stream'

class HTMLEncException(Exception):
    pass

def encrypt(filename, password, mimetype=None, linelength=128):
    """
    optional mimetype. if not provided, tries to get one from filename
    options linelength, controls look of output html
    """

    # Open the file.
    try:
        filehandle = open(filename, 'rb')
    except (IOError, OSError) as e:
        raise HTMLEncException(str(e))

    # Get mimetype if not provided.
    if mimetype is None:
        mimetype, _ = mimetypes.guess_type(filename)
        if mimetype is None:
            mimetype = DEFAULT_MIMETYPE

    # Read the entire file.
    # Could be streaming, but for now buffer entire thing.
    plaintext = filehandle.read()
    filehandle.close()

    # Perform the encryption.
    unencrypted_content = file_content.UnencryptedContent(plaintext, mimetype)
    encrypted_content = unencrypted_content.encrypt(password)

    # Generate html file
    wrapper = html_wrapper.HTMLWrapper(linelength=linelength)
    html_string = wrapper.wrap(encrypted_content)

    # Return the html string.
    return html_string

def decrypt(filename, password):
    """
    filename is path to html file
    TODO: version the html files for compatibility?
    """

    # Open the file
    try:
        filehandle = open(filename, 'r')
    except (IOError, OSError) as e:
        raise HTMLEncException(str(e))

    # Read it in.
    html_string = filehandle.read()
    filehandle.close()

    # Unwrap the ciphertext.
    wrapper = html_wrapper.HTMLWrapper()
    encrypted_content = wrapper.unwrap(html_string)

    # Decrypt it.
    unencrypted_content = encrypted_content.decrypt(password)
    return unencrypted_content

if __name__ == "__main__":

    action = sys.argv[1]
    args = sys.argv[2:4]

    if action == 'encrypt':
        sys.stdout.write(encrypt(*args))
    elif action == 'decrypt':
        sys.stdout.write(decrypt(*args).plaintext)
    else:
        raise HTMLEncException('Unknown action: %s' % action)
    