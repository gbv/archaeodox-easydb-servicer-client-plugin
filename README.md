# archaeoDox EasyDB Servicer Client

This plugin is part of the archaeoDox system and allows redirecting EasyDB [server callbacks](https://docs.easydb.de/en/technical/plugins/#server-callbacks) to an external [servicer instance](https://github.com/gbv/archaeodox-servicer).
It allows to route individual callbacks for each object type.

# Installation

1. Go to the EasyDB plugin directory and clone this repository.

2. Load the submodule [easydb-library](https://github.com/programmfabrik/easydb-library):

```
git submodule update --init --recursive
```

3. Create translation files:

```
make .
```

4. Restart EasyDB:

```
docker restart easydb-server
```