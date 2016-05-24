.. :changelog:

Release History
---------------

0.3.5 (2016-05-24)
++++++++++++++++++

**Bugfixes**

- All output from ia-mine should be JSONL.
  Some responses from the Metadata API contain unescaped newlines.
  This causes a lot of issues when using `jq` are when parsing JSON line-by-line.
  to address this, JSON responses returned from server are now parsed and dumped back to JSON before printing to stdout.


0.3.5 (2016-05-24)
++++++++++++++++++

**Features and Improvements**

- Fixed ``Exception ignored in:`` errors.
- Added support for custom config files.

0.3.3 (2015-08-04)
++++++++++++++++++

**Bugfixes**

-  Added HISTORY.rst to MANIFEST.in to fix `pip install iamine`.

0.3.2 (2015-08-03)
++++++++++++++++++

**Bugfixes**

-  ``asyncio.JoinableQueue`` was deprecated in Python 3.4.4.
   ``iamine.core.Miner`` now uses ``asyncio.Queue`` for Python 3.4.4 and
   newer and ``asyncio.JoinableQueue`` for older versions
   (``asyncio.Queue`` cannot be used for all versions because
   ``asyncio.Queue.join()`` was only added in version 3.4.4.).
-  ``SearchMiner.get_search_info()`` is no longer a coroutine (now uses
   ``urllib``). Fixed bug in ``iamine.api.search`` where it was still
   being called as coroutine.
