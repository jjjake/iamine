VERSION=$(shell grep -m1 version iamine/__init__.py | cut -d\' -f2)
UNAME=$(shell uname)

ifeq ($(UNAME), Darwin)
    OS=macosx
else
    OS=linux
endif


publish:
	python3 setup.py register
	python3 setup.py sdist upload

clean-pex:
	rm -fr ia-pex "$$HOME/.pex/install/*" "$$HOME/.pex/build/*"

binaries: clean-pex
	pex -vvv --python=python3.3 --source-dir=. --entry-point=iamine:main --pex-name=ia-mine-$(VERSION)-$(OS)-py3.3.pex
	pex -vvv --python=python3.4 --source-dir=. --entry-point=iamine:main --pex-name=ia-mine-$(VERSION)-$(OS)-py3.4.pex

publish-binaries: 
	wget -nc https://archive.org/download/ia-pex/ia-0.7.9-python2.7.pex
	chmod +x ia-0.7.9-python2.7.pex
	./ia-0.7.9-python2.7.pex upload iamine-pex ia-mine-$(VERSION)-py3.3.pex ia-mine-$(VERSION)-py3.4.pex

