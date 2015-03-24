=========
 IA Mine
=========

Internet Archive data mining tools.


What Is IA Mine?
================

IA Mine is a command line tool and Python 3 library for data mining
the Internet Archive.

**Note: Documentation currently in progress.**


How Do I Get Started?
=====================


Command Line Interface
----------------------

The IA Mine command line tool should work on any Unix-like operating
system that has Python 3 installed on it. To start using ``ia-mine``,
simply download one of the latest binaries from
`https://archive.org/details/iamine-pex
<https://archive.org/details/iamine-pex>`_.

.. code:: bash

    # Download ia-mine and make it executable.
    $ curl -L https://archive.org/download/iamine-pex/ia-mine-0.2.0.pex > ia-mine
    $ chmod +x ia-mine
    $ ./ia-mine -v
    0.2.0
    

Python Library
--------------

The IA Mine Python library can be installed with pip:

.. code:: bash

    # Create a Python 3 virtualenv, and install iamine.
    $ virtualenv --python=python3 venv
    $ . venv/bin/activate
    $ pip install iamine

This will also install the ``ia-mine`` comand line tool into your virtualenv:

.. code:: bash

    $ which ia-mine
    /home/user/venv/bin/ia-mine


Data Mining with IA Mine and jq
===============================

``ia-mine`` simply retrieves metadata and search results concurrently
from Archive.org, and dumps the JSON returned to stdout and any error
messages to stderr. Mining the JSON dumped to stdout can be done using a
tool like `jq <http://stedolan.github.io/jq/>`_, for example. jq
binaries can be downloaded at `http://stedolan.github.io/jq/download/
<http://stedolan.github.io/jq/download/>`_.

``ia-mine`` can mine Archive.org search results, the items returned from
search results, or items provide via an itemlist or stdin.


Developers
==========

Please report any bugs or issues on github:
`https://github.com/jjjake/iamine <https://github.com/jjjake/iamine>`_
