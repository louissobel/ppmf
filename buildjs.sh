set -e

# fucking stupid I need this, gluejs buggy, throws error otherwise
rm -rf ~/.gluejs-cache

echo "Linting"

jshint js/

echo "Compiling"

gluejs  --include ./js \
	--global HtmlEncController \
	--main js/html_enc_controller.js \
	--nocache \
	| \
cat > templates/main.js
