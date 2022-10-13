L10N_FILES = l10n/servicer-client.csv
PLUGIN_NAME = servicer-client
PLUGIN_PATH = 
INSTALL_FILES = \
	src/server/servicer.client.py \
	src/server/settings.py \
	src/server/wfs_client.py \
	manifest.yml \
	$(WEB)/l10n/cultures.json \
	$(WEB)/l10n/de-DE.json \
	$(WEB)/l10n/en-US.json \

all: build

include easydb-library/tools/base-plugins.make

build: code

code: $(L10N)

clean: clean-base
