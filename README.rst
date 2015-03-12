=========
 IA Mine
=========
-------------------------------------
 Internet Archive data mining tools.
-------------------------------------


What Is IA Mine?
================

IA Mine is a command line tool and Python 3 library for data mining
the Internet Archive. Note: documentation in progress.


How Do I Get Started?
=====================

Command Line Interface
----------------------

The IA Mine command line tool should work on any Unix-like operating
system that has Python 3 installed on it. To start using the IA Mine
command line tool, simply download one of the latest binaries from
`https://archive.org/details/iamine-pex
<https://archive.org/details/iamine-pex>`_. Currently, ``ia-mine``
binaries are dependent on the Python 3 minor version you have
installed.

For example, if you have Python 3.4 installed on your operating system,
you would download an ``ia-mine`` py3.4 binary.


.. code:: bash

    # Download ia-mine and make it executable.
    $ curl -L https://archive.org/download/iamine-pex/ia-mine-0.1.3-py3.3.pex > ia-mine
    $ chmod +x ia-mine
    $ ./ia-mine -v
    0.1.3
    

Data Mining with IA Mine and jq
```````````````````````````````

``ia-mine`` simply retrieves metadata and search results concurrently
from Archive.org, and dumps the JSON returned to stdout and any error
messages to stderr. Mining the JSON dumped to stdout can be done using a
tool like `jq <http://stedolan.github.io/jq/>`_, for example. jq
binaries can be downloaded at `http://stedolan.github.io/jq/download/
<http://stedolan.github.io/jq/download/>`_.
