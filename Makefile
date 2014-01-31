
js_core_deps = js/core/*
decrypt_js_deps = $(js_core_deps) js/decrypt/*
encrypt_js_deps = $(js_core_deps) js/encrypt/*

css_core_deps = css/common.less css/bootstrap.css

demo_file = img/demo.jpg
demo_password = password

all: webapp demo

demo: pages/demo.html

webapp: pages/encrypt.html

pages/encrypt.html: pages/ templates/encrypt.html templates/decrypt.html build/encrypt_controller.js build/encrypt.css
	bin/build_jinja templates/encrypt.html pages/encrypt.html

pages/demo.html: pages/ templates/decrypt.html $(demo_file)
	python html_enc.py encrypt $(demo_file) $(demo_password) > pages/demo.html

templates/decrypt.html: templates/decrypt_proto.html build/decrypt_controller.js build/decrypt.css
	bin/build_jinja templates/decrypt_proto.html templates/decrypt.html

build/encrypt_controller.js: build/ $(encrypt_js_deps)
	bin/build_js js/encrypt/encrypt_controller.js EncryptController build/encrypt_controller.js

build/decrypt_controller.js: build/ $(decrypt_js_deps)
	bin/build_js js/decrypt/decrypt_controller.js DecryptController build/decrypt_controller.js

build/decrypt.css: css/decrypt.less $(css_core_deps)
	lessc css/decrypt.less build/decrypt.css

build/encrypt.css: css/encrypt.less $(css_core_deps)
	lessc css/encrypt.less build/encrypt.css


pages/:
	mkdir -p pages/

build/:
	mkdir -p build/

.PHONY: clean
clean:
	rm -rf pages/
	rm -rf build/
	rm -f templates/decrypt.html

.PHONY: deploy
deploy: webapp
	bin/deploy
