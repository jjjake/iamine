VERSION=$(shell grep -m1 version iamine/_version.py | cut -d\' -f2)

IA_PEX_DESCRIPTION="<p>This item contains binaries of the ia-mine command line tool. \"ia-mine\" is a command line tool for concurrently retrieving metadata from Archive.org items. All binaries were built using <a href=\"https://github.com/pantsbuild/pex\" rel=\"nofollow\">https://github.com/pantsbuild/pex</a>.</p><br /><p>Latest binaries:<br /><a href=\"/download/iamine-pex/ia-mine-${VERSION}-py3.3.pex\">ia-mine v${VERSION}-py3.3.pex</a><br /><a href=\"/download/iamine-pex/ia-mine-${VERSION}-py3.4.pex\">ia-mine v${VERSION}-py3.4.pex</a><br /></p><p>All binaries: <a href=\"/download/iamine-pex\" rel=\"nofollow\">archive.org/download/iamine-pex</a></p><br /><p>Github repository: <a href=\"https://github.com/jjjake/iamine\" rel=\"nofollow\">https://github.com/jjjake/iamine</a></p>"

publish:
	python3 setup.py register
	python3 setup.py sdist upload

clean-pex:
	rm -fr ia-pex "$$HOME/.pex/install/*" "$$HOME/.pex/build/*"

wheels:
	rm -rf wheelhouse
	pip3 wheel .
	pip3.3 wheel -r requirements.txt

binaries: clean-pex wheels
	pex -vvv --python=python3.3 --no-pypi --repo=wheelhouse/ -r docopt -r asyncio -r iamine -e iamine.ia_mine:main --pex-name=ia-mine-$(VERSION)-py3.3.pex
	pex -vvv --python=python3.4 --no-pypi --repo=wheelhouse/ -r docopt -r iamine -e iamine.ia_mine:main --pex-name=ia-mine-$(VERSION)-py3.4.pex

publish-binaries:
	wget -nc https://archive.org/download/ia-pex/ia-0.7.9-python2.7.pex
	chmod +x ia-0.7.9-python2.7.pex
	./ia-0.7.9-python2.7.pex upload iamine-pex ia-mine-$(VERSION)-py3.3.pex ia-mine-$(VERSION)-py3.4.pex
	./ia-0.7.9-python2.7.pex metadata iamine-pex -m description:$(IA_PEX_DESCRIPTION) -m version:$(VERSION)
