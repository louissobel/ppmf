
js_core_deps = js/core/*
decrypt_js_deps = $(js_core_deps) js/decrypt/*
encrypt_js_deps = $(js_core_deps) js/encrypt/*

css_core_deps = css/common.less css/bootstrap.css

demo_file = img/demo.jpg
demo_password = password

all: webapp demo

demo: pages/demo.html

webapp: pages/encrypt.html pages/decrypt_template.html

pages/encrypt.html: pages/ templates/encrypt.html pages/decrypt_template.html build/encrypt_controller.js build/encrypt.css
	bin/build_jinja templates/encrypt.html pages/encrypt.html

pages/demo.html: pages/ pages/decrypt_template.html $(demo_file)
	node js/ppmf.js --encrypt $(demo_file) --password $(demo_password) --outfile pages/demo.html --template pages/decrypt_template.html --quiet

pages/decrypt_template.html: templates/decrypt_proto.html build/decrypt_controller.js build/decrypt.css
	bin/build_jinja templates/decrypt_proto.html pages/decrypt_template.html

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

.PHONY: deploy
deploy: webapp
	bin/deploy
