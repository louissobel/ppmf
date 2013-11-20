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

HTML_TEMPLATE = """
<html>
    <head>
    <title>Encrypted File</title>

    <script type="text/javascript">
        var decrypt = function (ciphertext, password) {
            var firstNewline = ciphertext.indexOf('\\n');
            return ciphertext.substring(firstNewline + 1);
        };

        var setUp = function () {
            var ciphertextHolder = document.getElementById('ciphertext')
              , plaintextHolder = document.getElementById('plaintext')
              , decryptButton = document.getElementById('decrypt')
              ;

            decryptButton.addEventListener('click', function () {
                plaintextHolder.textContent = decrypt(ciphertextHolder.textContent);
            });
        };
    </script>
    </head>

    <body onload="setUp()">
    <div>
        <button id='decrypt'>Decrypt</button>
    </div>
    <div>
        <pre id="ciphertext">%s</pre>
    </div>
    <div>
        <pre id="plaintext"></pre>
    </div>
    </body>
</html>
"""

def wrap(ciphertext):
    """
    returns html string wrapping the ciphertext
    """
    return HTML_TEMPLATE % ciphertext

def unwrap(html_string):
    """
    gets the cipher text back out of this
    """
    match = re.search(r'\<pre id="ciphertext"\>(.*?)\</pre\>', html_string, re.DOTALL)
    if not match:
        raise ValueError
    else:
        return match.group(1)

if __name__ == "__main__":
    import sys

    source = sys.stdin.read()
    if sys.argv[1] == 'wrap':
        print wrap(source)
    elif sys.argv[1] == 'unwrap':
        print unwrap(source)
    else:
        raise ValueError
