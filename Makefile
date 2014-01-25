all: templates/html_enc_controller.js

templates/html_enc_controller.js: js/*
	./buildjs.sh
