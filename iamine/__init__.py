#!/usr/bin/env python3
"""
IA Mine
~~~~~~~

Concurrently retrieve metadata from Archive.org items.

:copyright: (c) 2015 by Internet Archive.
:license: AGPL 3, see LICENSE for more details.

"""

__title__ = 'iamine'
__version__ = '0.0.2'
__author__ = 'Jacob M. Johnson'
__license__ = 'AGPL 3'
__copyright__ = 'Copyright 2015 Internet Archive'


import argparse
import logging
import signal
import os
import sys
import asyncio
import random

import aiohttp


class Miner:

    def __init__(self, identifiers, loop, done_callback=None, maxtasks=None, cache=None,
                 retries=None, secure=None, hosts=None):
        # Set default values for kwargs.
        maxtasks = 100 if not maxtasks else maxtasks
        # By default, don't cache item metadata in redis.
        params = {'dontcache': 1} if not cache else {}
        max_retries = 10 if not retries else retries
        protocol = 'http://' if not secure else 'https://'

        self.identifiers = identifiers
        self.loop = loop
        self.tasks = set()
        self.busy = set()
        self.done_callback = done_callback
        self.sem = asyncio.Semaphore(maxtasks)

        self.params = params
        self.protocol = protocol
        self.hosts = hosts
        self.max_retries = max_retries
        self.connector = aiohttp.TCPConnector(share_cookies=True, loop=loop)

        self.all_tasks_queued = False

    @asyncio.coroutine
    def run(self):
        asyncio.Task(self.addurls(self.identifiers))  # Set initial work.
        yield from asyncio.sleep(1)
        while self.tasks or self.all_tasks_queued is False:
            yield from asyncio.sleep(1)
        self.connector.close()
        self.loop.stop()

    def _done_callback(self, future):
        resp = future.result()
        resp.content = resp._content
        if self.done_callback:
            self.done_callback(resp)
        else:
            print(resp.content.decode('utf-8'))

    @asyncio.coroutine
    def addurls(self, identifiers):
        for identifier in identifiers:
            if not identifier.strip():
                continue
            yield from self.sem.acquire()
            task = asyncio.Task(self.process(identifier.strip()))
            task.add_done_callback(lambda t: self.sem.release())
            task.add_done_callback(self._done_callback)
            task.add_done_callback(self.tasks.remove)
            self.tasks.add(task)
        self.all_tasks_queued = True

    @asyncio.coroutine
    def process(self, identifier):
        if self.hosts:
            host = self.hosts[random.randrange(len(self.hosts))]
        else:
            host = 'archive.org'
        url = self.protocol + host + '/metadata/' + identifier
        retry = 0
        while True:
            retry += 1
            try:
                resp = yield from aiohttp.request(
                    'get', url, params=self.params, connector=self.connector)
                yield from resp.read()
                resp.close()
                return resp
            except Exception as exc:
                sys.stderr.write('{0} has error {1}\n'.format(url, repr(exc)))
                if retry >= self.max_retries:
                    return
                sys.stderr.write(
                    '... retry {0}/{1} {2}\n'.format(retry, self.max_retries, url))
                yield from asyncio.sleep(1)


def main():
    parser = argparse.ArgumentParser(
        description='''Concurrently retrieve metadata from Archive.org items.''')

    parser.add_argument('itemlist', nargs='?', default=sys.stdin, 
                        type=argparse.FileType('r'),
                        help='''A file containing Archive.org identifiers, one per line,
                                for which to retrieve metadata from. If no itemlist is
                                provided, identifiers will be read from stdin.''')
    parser.add_argument('--version', '-v', action='version', 
                        version='%(prog)s {}'.format(__version__))
    parser.add_argument('--workers', '-w', type=int, default=100,
                        help='''The maximum number of tasks to run at once. 
                                Defaults to 100''')
    parser.add_argument('--cache', '-c', action='store_true',
                        help='''Cache item metadata on Archive.org. 
                                Items are not cached are not cached by default.''')
    parser.add_argument('--retries', '-r', type=int, default=10,
                        help='The maximum number of retries for each item.')
    parser.add_argument('--secure', '-s', action='store_true',
                        help='Use HTTPS. HTTP is used by default.')
    parser.add_argument('--hosts', type=argparse.FileType('r'),
                        help='''A file containing a list of hosts to shuffle through. 
                                Default host is archive.org''')
    args = parser.parse_args()

    if args.hosts:
        hosts = [x.strip() for x in args.hosts if x.strip()]
    else:
        hosts = None

    if args.itemlist is sys.stdin:
        if (not os.fstat(sys.stdin.fileno()).st_size > 0) and (sys.stdin.seekable()):
            # Exit with 2 if stdin appears to be empty.
            sys.exit(2)

    loop = asyncio.get_event_loop()
    m = Miner(args.itemlist, loop, maxtasks=args.workers, cache=args.cache,
              retries=args.retries, secure=args.secure, hosts=hosts)
    asyncio.Task(m.run())

    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
    except RuntimeError:
        pass

    loop.run_forever()


if __name__ == '__main__':
    main()
