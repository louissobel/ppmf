
js_core_deps = js/core/*
decrypt_js_deps = $(js_core_deps) js/decrypt/*
encrypt_js_deps = $(js_core_deps) js/encrypt/*

css_core_deps = css/common.less css/bootstrap.css img/gun_metal.png

demo_file = img/example.jpg
demo_password = password

main_page_deps = templates/encrypt_wrapper.html templates/_faq.html templates/_main.html build/encrypt_controller.js build/encrypt.css pages/decrypt_template.html

all: webapp demo

demo: pages/example.jpg__encrypted.html

encrypt: pages/encrypt.html

faq: pages/faq.html

favicon: pages/favicon.ico

webapp: encrypt pages/decrypt_template.html demo favicon faq

pages/encrypt.html: pages/ templates/encrypt.html $(main_page_deps)
	bin/build_jinja templates/encrypt.html pages/encrypt.html

pages/faq.html: pages/ templates/faq.html $(main_page_deps)
	bin/build_jinja templates/faq.html pages/faq.html

pages/example.jpg__encrypted.html: pages/ pages/decrypt_template.html $(demo_file) js/ppmf.js
	node js/ppmf.js --encrypt $(demo_file) --password $(demo_password) --outfile pages/example.jpg__encrypted.html --template pages/decrypt_template.html --quiet

pages/decrypt_template.html: pages/ templates/decrypt_proto.html build/decrypt_controller.js build/decrypt.css
	bin/build_jinja templates/decrypt_proto.html pages/decrypt_template.html

pages/favicon.ico: img/favicon.ico
	cp img/favicon.ico pages/favicon.ico

build/encrypt_controller.js: build/ $(encrypt_js_deps)
	bin/build_js js/encrypt/encrypt_controller.js EncryptController build/encrypt_controller.js

build/decrypt_controller.js: build/ $(decrypt_js_deps)
	bin/build_js js/decrypt/decrypt_controller.js DecryptController build/decrypt_controller.js

build/decrypt.css: css/decrypt.less $(css_core_deps)
	bin/build_less css/decrypt.less build/decrypt.css

build/encrypt.css: css/encrypt.less $(css_core_deps)
	bin/build_less css/encrypt.less build/encrypt.css


pages/:
	mkdir -p pages/

build/:
	mkdir -p build/

.PHONY: clean
clean:
	rm -rf pages/
	rm -rf build/

.PHONY: deploy
deploy:
	bin/deploy

.PHONY: server
server:
	cd pages/ && python -m SimpleHTTPServer
