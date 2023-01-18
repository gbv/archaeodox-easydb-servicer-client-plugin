# Easydb Servicer Client

This plugin allows you to redirect easydb [server callbacks](https://docs.easydb.de/en/technical/plugins/#server-callbacks) to an external [servicer instance](https://github.com/chris-jan-trapp/flask_servicer).
It allows to route individual callbacks for each data type.

# Requirements

**NOTE** This guy contains the programmfabrik easydb-library as submodule. If `make`ing the l10n fails after cloning this repo, you need to initialize the submodule by:

```
git submodule update --init --recursive
```

Or you can do the initial cloning via

```
git clone --recursive https://github.com/gbv/archaeodox-easydb-servicer-client-plugin.git
```
