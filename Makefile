VERSION=$(shell grep -m1 version iamine/__init__.py | cut -d\' -f2)

publish:
	python3 setup.py register
	python3 setup.py sdist upload

clean-pex:
	rm -fr ia-pex "$$HOME/.pex/install/*" "$$HOME/.pex/build/*"

wheels:
	pip3.3 wheel aiohttp==0.13.1 asyncio==3.4.1 .
	curl -L 'https://pypi.python.org/packages/py3/a/aiohttp/aiohttp-0.13.1-py3-none-any.whl' > wheelhouse/aiohttp-0.13.1-py3-none-any.whl # Download universal aiohttp wheel.

binaries: clean-pex wheels
	pex -vvv --python=python3.3 --no-pypi --repo=wheelhouse/ -r asyncio -r iamine -e iamine:main --pex-name=ia-mine-$(VERSION)-py3.3.pex
	pex -vvv --python=python3.4 --no-pypi --repo=wheelhouse/ -r iamine -e iamine:main --pex-name=ia-mine-$(VERSION)-py3.4.pex

publish-binaries: 
	wget -nc https://archive.org/download/ia-pex/ia-0.7.9-python2.7.pex
	chmod +x ia-0.7.9-python2.7.pex
	./ia-0.7.9-python2.7.pex upload iamine-pex ia-mine-$(VERSION)-py3.3.pex ia-mine-$(VERSION)-py3.4.pex

