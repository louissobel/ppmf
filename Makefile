all: templates/main.js

templates/main.js: js/*
	./buildjs.sh
