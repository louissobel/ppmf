Password Protect My File
===============

Source code for https://www.passwordprotectmyfile.com
--------------

### Building

 1. `bin/check_deps` will check that all dependencies are satisfied
 2. `make webapp` will build the site pages, putting the output into `pages/`

### Dependencies for build

#### Quick install:

`pip install -r requirements.txt`

`npm install -g`

#### Details:

Executables in `$PATH`

 - `python`
 - `slimit`
 - `jshint`
 - `lessc`
 - `browserify`

`requirements.txt` has the python requirements (`slimit` and `jinja2`)

`package.json` _in the top level_ contains the node.js packages whose executables are required.

`bin/check_deps` will check that all requirements are satisfied.

### Comparing Website to the code in this repo

`bin/check_production_sha`

To confirm that the code in the html page you're viewing online does in fact correspond to the code in this repo,
there is a revision system in place. The pages online have a "Revision \d+" in the footer. The above script downloads
the current page, checks out the corresponding revision tag, computes the two shasums and compares them.

### ppmf command line utility

The root of the ppmf utility on npm is in `js/`.
