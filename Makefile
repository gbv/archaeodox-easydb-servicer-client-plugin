PLUGIN_NAME = servicer-client
PLUGIN_PATH = 
INSTALL_FILES = \
	src/server/servicer.client.py \
	src/server/settings.py \
	src/server/wfs_client.py \
	manifest.yml


all: build

include easydb-library/tools/base-plugins.make

build: code css npm_install updater

updater:
	./node_modules/webpack/bin/webpack.js --config src/update/webpack.config.js

npm_install:
	npm install
	cp -r node_modules build/node_modules

code: $(JS) $(L10N) $(WEBHOOK_JS)

clean: clean-base
