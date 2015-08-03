VERSION=$(shell grep -m1 version iamine/__init__.py | cut -d\' -f2)

IA_PEX_DESCRIPTION="<p>This item contains binaries of the ia-mine command line tool. \"ia-mine\" is a command line tool for concurrently retrieving metadata from Archive.org items. All binaries were built using <a href=\"https://github.com/pantsbuild/pex\" rel=\"nofollow\">https://github.com/pantsbuild/pex</a>.</p><br /><p>Latest binary: <a href=\"/download/iamine-pex/ia-mine-${VERSION}-py3.pex\">ia-mine v${VERSION}</a></p><br /><p>Github repository: <a href=\"https://github.com/jjjake/iamine\" rel=\"nofollow\">https://github.com/jjjake/iamine</a></p>"

publish:
	python3 setup.py register
	python3 setup.py sdist upload

clean-pex:
	rm -fr ia-pex "$$HOME/.pex/install/*" "$$HOME/.pex/build/*"

wheels:
	rm -rf wheelhouse
	pip3 wheel .
	pip3 wheel -r requirements.txt

binaries: clean-pex wheels
	pex -vvv --disable-cache --no-pypi --repo=wheelhouse/ --python-shebang='/usr/bin/env python3' -r requirements.txt -e iamine.__main__:main -o ia-mine-$(VERSION)-py3.pex

publish-binaries:
	wget -nc https://archive.org/download/ia-pex/ia-0.7.9-python2.7.pex
	chmod +x ia-0.7.9-python2.7.pex
	./ia-0.7.9-python2.7.pex upload iamine-pex ia-mine-$(VERSION)-py3.pex
	./ia-0.7.9-python2.7.pex metadata iamine-pex -m description:$(IA_PEX_DESCRIPTION) -m version:$(VERSION)
