# [Changelog](https://github.com/jjjake/iamine/releases)

## [0.3.1](https://github.com/jjjake/iamine/compare/0.3.1...0.3.1)

* [6f49430](https://github.com/jjjake/iamine/commit/6f49430) v0.3.0
* [053053d](https://github.com/jjjake/iamine/commit/053053d) Updated pex-binary creation.
* [2ac4eed](https://github.com/jjjake/iamine/commit/2ac4eed) Use query `all:1` to return all indexed items, rather than `(*:*)` which returns all indexed documents (which includes forumposts which aren't real items!).
* [7af9ec7](https://github.com/jjjake/iamine/commit/7af9ec7) S3-keys now required. Added check to confirm key pairs are valid before any mining occurs!
* [2cc61dd](https://github.com/jjjake/iamine/commit/2cc61dd) Added exception hook to handle exceptions rasied in the CLI.
* [12743a1](https://github.com/jjjake/iamine/commit/12743a1) Close connections...
* [e484c3e](https://github.com/jjjake/iamine/commit/e484c3e) Removed sort options. Added --debug
* [479eb6d](https://github.com/jjjake/iamine/commit/479eb6d) Added configure() to __all__
* [07099b4](https://github.com/jjjake/iamine/commit/07099b4) Do not auto-sort search results.
* [dc494f3](https://github.com/jjjake/iamine/commit/dc494f3) Updated ia-mine version in examples.
* [01f2821](https://github.com/jjjake/iamine/commit/01f2821) Use patched version of pex to support custom hashbang (support for universal Python3 binary).
* [2227b43](https://github.com/jjjake/iamine/commit/2227b43) use pip not pip3.3
* [51f41c6](https://github.com/jjjake/iamine/commit/51f41c6) v0.2.2
* [e08596b](https://github.com/jjjake/iamine/commit/e08596b) Wheel is not universal, Python3 only.
* [8bf9cb9](https://github.com/jjjake/iamine/commit/8bf9cb9) Changed default search rows from 1000 to 500.
* [1433e0d](https://github.com/jjjake/iamine/commit/1433e0d) Removed --sort param as it is too expensive to be useful in the iamine client, and can cause a lot of issues for the Archive.org SE.
* [c655b3f](https://github.com/jjjake/iamine/commit/c655b3f) v0.2.1
* [d756e8e](https://github.com/jjjake/iamine/commit/d756e8e) Do not do any auto-sorting of search results. The sorting cost is too much, for both the ia-mine client and the Archive.org SE.
* [c54dd33](https://github.com/jjjake/iamine/commit/c54dd33) Refactored Miner to be a base class for other Mine classes such as ItemMiner SearchMiner. Added iamine.requests module to handle all requests logic. Refactored requests logic to retry on all exceptions, even exceptions raised in callbacks.
* [1a45b6e](https://github.com/jjjake/iamine/commit/1a45b6e) v0.3.0
* [6d698ff](https://github.com/jjjake/iamine/commit/6d698ff) Updated README
* [ebd9c4e](https://github.com/jjjake/iamine/commit/ebd9c4e) v0.2.0
* [a0f3a18](https://github.com/jjjake/iamine/commit/a0f3a18) Updated README
* [9c353a7](https://github.com/jjjake/iamine/commit/9c353a7) Fixed empty cookies/locale bugs.
* [808fb30](https://github.com/jjjake/iamine/commit/808fb30) Renamed iamine.ia_mine to iamine.__main__
* [6a6f079](https://github.com/jjjake/iamine/commit/6a6f079) Handle cases where no locale is set on system (for UA string setting). removed _version module.
* [23af82c](https://github.com/jjjake/iamine/commit/23af82c) Refactored Mine for more general use. Added mine_urls method to API for mining any given URL. Added dosctrings (in progress still).
* [236072c](https://github.com/jjjake/iamine/commit/236072c) Added rate limiting, can be tuned here: https://archive.org/metadata/iamine-rate-limiter/metadata/rate_per_second
* [f484278](https://github.com/jjjake/iamine/commit/f484278) Refactor to replace any usage of urllib/http.cookies with asyncio.
* [87baa87](https://github.com/jjjake/iamine/commit/87baa87) Added Developers section.
* [f4eee83](https://github.com/jjjake/iamine/commit/f4eee83) Added Developers section.
* [0f83daf](https://github.com/jjjake/iamine/commit/0f83daf) Added sort param for sorting search results. Refactored search() to be more friendly for large sets of search results.
* [a854dcc](https://github.com/jjjake/iamine/commit/a854dcc) v0.1.5
* [d02548e](https://github.com/jjjake/iamine/commit/d02548e) Updated README
* [20f997c](https://github.com/jjjake/iamine/commit/20f997c) Update README.rst
* [6decaba](https://github.com/jjjake/iamine/commit/6decaba) Update README.rst
* [346ac9d](https://github.com/jjjake/iamine/commit/346ac9d) I forgot pathlib is not in the standar lib in Python 3.3... use os instead for now.
* [a98a107](https://github.com/jjjake/iamine/commit/a98a107) Return an empty dict for invalid search queries rather than None. Hopefully in the future the search API will either return a JSON error message or a non 200 HTTP status code!
* [9d835a9](https://github.com/jjjake/iamine/commit/9d835a9) Allow --field to be specified with --info.
* [62de5a5](https://github.com/jjjake/iamine/commit/62de5a5) Make sure "identifier" is always returned in search results.
* [cd99b47](https://github.com/jjjake/iamine/commit/cd99b47) Added --info and --num-found args to ia-mine for returning info about given search query.
* [1cb6bed](https://github.com/jjjake/iamine/commit/1cb6bed) Suppress BrokenPipeError exception messages.
* [193c438](https://github.com/jjjake/iamine/commit/193c438) updated readme
* [f5b5a1e](https://github.com/jjjake/iamine/commit/f5b5a1e) updated readme
* [0c2e269](https://github.com/jjjake/iamine/commit/0c2e269) updated readme
* [b640162](https://github.com/jjjake/iamine/commit/b640162) updated readme
* [e151801](https://github.com/jjjake/iamine/commit/e151801) updated readme
* [ea79230](https://github.com/jjjake/iamine/commit/ea79230) updated readme
* [45e5e4b](https://github.com/jjjake/iamine/commit/45e5e4b) Fixed rst typo
* [719fd26](https://github.com/jjjake/iamine/commit/719fd26) Fixed rst typo
* [c834349](https://github.com/jjjake/iamine/commit/c834349) Added user-agent header to all requests. Added ability to configure ia-mine to send cookies with each request. Added utils and exceptions modules. Other refactoring.
* [26c3846](https://github.com/jjjake/iamine/commit/26c3846) v0.1.3
* [5fd67d6](https://github.com/jjjake/iamine/commit/5fd67d6) Removed "raise exc" from make_request().
* [2c804f4](https://github.com/jjjake/iamine/commit/2c804f4) Set encoding parameter="utf-8" in aiohttp.request.json() method to avoid using chardet.
* [d2f7715](https://github.com/jjjake/iamine/commit/d2f7715) v0.1.1
* [3d86c89](https://github.com/jjjake/iamine/commit/3d86c89) Added --itemlist option. Supress tracebacks for keyboard interrupts.
* [80fd851](https://github.com/jjjake/iamine/commit/80fd851) Added callback option for processing search results.
* [d45ae3e](https://github.com/jjjake/iamine/commit/d45ae3e) Ignore RuntimeError exceptions.
* [1485da8](https://github.com/jjjake/iamine/commit/1485da8) Ignore RuntimeError exceptions.
* [8cf0e53](https://github.com/jjjake/iamine/commit/8cf0e53) Added ability to mine search results. Other cleanup.
* [4d0e323](https://github.com/jjjake/iamine/commit/4d0e323) ignore virtualenv stuff
* [060b33f](https://github.com/jjjake/iamine/commit/060b33f) Refactoring iamine.ia_mine and binary creation to be more pex friendly.
* [10671f2](https://github.com/jjjake/iamine/commit/10671f2) Require docopt
* [7da9111](https://github.com/jjjake/iamine/commit/7da9111) Moved core functionality to iamine.core, api to iamine.api, and ia-wrapper plugin script to iamine.ia_mine.
* [5a3233b](https://github.com/jjjake/iamine/commit/5a3233b) Update description when publishing binaries to archive.org.
* [d7c422a](https://github.com/jjjake/iamine/commit/d7c422a) ignore wheelhouse
* [53fdd7d](https://github.com/jjjake/iamine/commit/53fdd7d) ignore pex files
* [b61120f](https://github.com/jjjake/iamine/commit/b61120f) binaries target now makes universal binaries!
* [0eee02a](https://github.com/jjjake/iamine/commit/0eee02a) Use v0.13.1 of aiohttp because it has a universal wheel which allows us to create universal binaries.
* [7374d86](https://github.com/jjjake/iamine/commit/7374d86) v0.4
* [303f766](https://github.com/jjjake/iamine/commit/303f766) Refactored Mine for more general use. Added mine function for easy calling of Mine.
* [e5c0b0b](https://github.com/jjjake/iamine/commit/e5c0b0b) Added Makefile
* [cff37f2](https://github.com/jjjake/iamine/commit/cff37f2) v0.3
* [fbec9b1](https://github.com/jjjake/iamine/commit/fbec9b1) Added --version CLI arg.
* [9427bc4](https://github.com/jjjake/iamine/commit/9427bc4) Fail if Python version is < 3. Only install asyncio if Python version is < 3.4.
* [02e232e](https://github.com/jjjake/iamine/commit/02e232e) Added all Mine kwargs to CLI. Refactored main.
* [7541256](https://github.com/jjjake/iamine/commit/7541256) v0.2
* [f71cabe](https://github.com/jjjake/iamine/commit/f71cabe) Refactored asyncio loop logic. Added retries, secure and hosts options.
* [2be16fe](https://github.com/jjjake/iamine/commit/2be16fe) Added licensing details, IA copyright, etc.
* [66ba7d2](https://github.com/jjjake/iamine/commit/66ba7d2) Better detection of empty stdin.
* [8d03334](https://github.com/jjjake/iamine/commit/8d03334) By default, don't cache item metadata in redis. Can be overriden with cache arg set to True.
* [2cce9fa](https://github.com/jjjake/iamine/commit/2cce9fa) pep8 cleanup
* [bc70f3f](https://github.com/jjjake/iamine/commit/bc70f3f) Renamed Crawler to Miner
* [5b32b63](https://github.com/jjjake/iamine/commit/5b32b63) do not add URL to todo while retrying
* [f034123](https://github.com/jjjake/iamine/commit/f034123) removed commented code not being used.
* [273e380](https://github.com/jjjake/iamine/commit/273e380) use archive.org
* [68da886](https://github.com/jjjake/iamine/commit/68da886) initial commit
* [5365879](https://github.com/jjjake/iamine/commit/5365879) Initial commit

