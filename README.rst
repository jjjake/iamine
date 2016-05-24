=========
 IA Mine
=========

Internet Archive data mining tools.


What Is IA Mine?
================

IA Mine is a command line tool and Python 3 library for data mining
the Internet Archive.


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
    $ curl -LO https://archive.org/download/iamine-pex/ia-mine
    $ chmod +x ia-mine
    $ ./ia-mine --help
    ...

Usage:

.. code::

    $ ia-mine --help
    Concurrently retrieve metadata from Archive.org items.

    usage: ia-mine (<itemlist> | -) [--debug] [--workers WORKERS] [--cache]
                   [--retries RETRIES] [--secure] [--hosts HOSTS]
           ia-mine [--all | --search QUERY] [[--info | --info --field FIELD...]
                   |--num-found | --mine-ids | --field FIELD... | --itemlist]
                   [--debug] [--rows ROWS] [--workers WORKERS] [--cache]
                   [--retries RETRIES] [--secure] [--hosts HOSTS]
           ia-mine [-h | --version | --configure]

    positional arguments:
      itemlist              A file containing Archive.org identifiers, one per
                            line, for which to retrieve metadata from. If no
                            itemlist is provided, identifiers will be read from
                            stdin.

    optional arguments:
      -h, --help            Show this help message and exit.
      -v, --version         Show program's version number and exit.
      --configure           Configure ia-mine to use your Archive.org credentials.
      -d, --debug           Turn on verbose logging [default: False]
      -a, --all             Mine all indexed items.
      -s, --search QUERY    Mine search results. For help formatting your query,
                            see: https://archive.org/advancedsearch.php
      -m, --mine-ids        Mine items returned from search results.
                            [default: False]
      -i, --info            Print search result response header to stdout and exit.
      -f, --field FIELD     Fields to include in search results.
      -i, --itemlist        Print identifiers only to stdout. [default: False]
      -n, --num-found       Print the number of items found for the given search
                            query.
      --rows ROWS           The number of rows to return for each request made to
                            the Archive.org Advancedsearch API. On slower networks,
                            it may be useful to use a lower value, and on faster
                            networks, a higher value. [default: 50]
      -w, --workers WORKERS
                            The maximum number of tasks to run at once.
                            [default: 100]
      -c, --cache           Cache item metadata on Archive.org. Items are not
                            cached are not cached by default.
      -r, --retries RETRIES
                            The maximum number of retries for each item.
                            [default: 10]
      --secure              Use HTTPS. HTTP is used by default.
      -H, --hosts HOSTS     A file containing a list of hosts to shuffle through.


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
