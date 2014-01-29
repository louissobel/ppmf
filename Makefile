all: webapp

js_core_deps = js/core/*
decrypt_js_deps = $(js_core_deps) js/decrypt/*
encrypt_js_deps = $(js_core_deps) js/encrypt/*

webapp: pages/encrypt.html

pages/encrypt.html: pages/ templates/encrypt.html templates/decrypt.html build/encrypt_controller.js
	bin/build_jinja templates/encrypt.html pages/encrypt.html

templates/decrypt.html: templates/decrypt_proto.html build/decrypt_controller.js
	bin/build_jinja templates/decrypt_proto.html templates/decrypt.html

build/encrypt_controller.js: build/ $(encrypt_js_deps)
	bin/build_js js/encrypt/controller.js EncryptController build/encrypt_controller.js

build/decrypt_controller.js: build/ $(decrypt_js_deps)
	bin/build_js js/decrypt/controller.js DecryptController build/decrypt_controller.js

pages/:
	mkdir -p pages/

build/:
	mkdir -p build/

.PHONY: clean
clean:
	rm -rf pages/
	rm -rf build/
	rm -f templates/decrypt.html
