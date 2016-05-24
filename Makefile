VERSION=$(shell grep -m1 version iamine/__init__.py | cut -d\' -f2)

IA_PEX_DESCRIPTION="<p>This item contains binaries of the ia-mine command line tool. \"ia-mine\" is a command line tool for concurrently retrieving metadata from Archive.org items. All binaries were built using <a href=\"https://github.com/pantsbuild/pex\" rel=\"nofollow\">https://github.com/pantsbuild/pex</a>.</p><br /><p>Latest binary: <a href=\"/download/iamine-pex/ia-mine\">ia-mine v${VERSION}</a></p><br /><p>Github repository: <a href=\"https://github.com/jjjake/iamine\" rel=\"nofollow\">https://github.com/jjjake/iamine</a></p><p>The binaries only requirements are that you have Python 3 installed on a unix-like operating system."

publish:
	python3 setup.py register
	python3 setup.py sdist upload

clean-pex:
	rm -fr ia-pex "$$HOME/.pex/install/*" "$$HOME/.pex/build/*"

wheels:
	rm -rf wheelhouse
	pip3 wheel .
	pip3 wheel -r requirements.txt

binaries: clean-pex
	pex iamine==$(VERSION) asyncio -o ia-mine-$(VERSION)-py3-none-any.pex --platform 'linux-x86_64' --platform 'macosx-10.11-x86_64' --python-shebang '/usr/bin/env python3' -e iamine.__main__:main --repo wheelhouse

publish-binaries:
	wget -nc https://archive.org/download/ia-pex/ia
	chmod +x ia
	./ia upload iamine-pex ia-mine-$(VERSION)-py3-none-any.pex
	./ia upload iamine-pex ia-mine-$(VERSION)-py3-none-any.pex --remote-name=ia-mine
	./ia upload iamine-pex ia-mine-$(VERSION)-py3-none-any.pex --remote-name=iamine
	./ia metadata iamine-pex -m description:$(IA_PEX_DESCRIPTION) -m version:$(VERSION)
