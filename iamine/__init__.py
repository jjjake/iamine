#!/usr/bin/env python3
"""
IA Mine
~~~~~~~

Concurrently retrieve metadata from Archive.org items.

:copyright: (c) 2015 by Internet Archive.
:license: AGPL 3, see LICENSE for more details.

"""

__title__ = 'iamine'
__version__ = '0.5'
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

    def __init__(self, uris, loop, response_callback=None, max_tasks=None,
                 cache=None, retries=None, secure=None, hosts=None, path=None):
        # Set default values for kwargs.
        max_tasks = 100 if not max_tasks else max_tasks
        # By default, don't cache item metadata in redis.
        params = {'dontcache': 1} if not cache else {}
        max_retries = 10 if not retries else retries
        protocol = 'http://' if not secure else 'https://'
        path = '/metadata/' if not path else '/{0}/'.format(path.strip('/\n'))

        self.uris = uris
        self.loop = loop
        self.tasks = set()
        self.response_callback = response_callback
        self.sem = asyncio.Semaphore(max_tasks)

        self.params = params
        self.response_callback = response_callback
        self.protocol = protocol
        self.hosts = hosts
        self.path = path
        self.max_retries = max_retries
        self.connector = aiohttp.TCPConnector(share_cookies=True, loop=loop)

        self.all_tasks_queued = False

    @asyncio.coroutine
    def run(self):
        asyncio.Task(self.addurls(self.uris))  # Set initial work.
        yield from asyncio.sleep(1)
        while self.tasks or self.all_tasks_queued is False:
            yield from asyncio.sleep(1)
        self.connector.close()
        self.loop.stop()

    @asyncio.coroutine
    def handle_response(self, resp):
        if self.response_callback:
            yield from self.response_callback(resp)
        else:
            content = yield from resp.read()
            resp.close()
            print(content.decode('utf-8'))

    @asyncio.coroutine
    def addurls(self, uris):
        for uri in uris:
            if not uri.strip():
                continue
            elif not uri.startswith('http'):
                path = self.path + uri.strip()
                url = self.make_url(path)
            else:
                url = uri
            yield from self.sem.acquire()
            task = asyncio.Task(self.make_request(url.strip()))
            task.add_done_callback(lambda t: self.sem.release())
            task.add_done_callback(self.tasks.remove)
            self.tasks.add(task)
        self.all_tasks_queued = True

    @asyncio.coroutine
    def make_request(self, url):
        retry = 0
        while True:
            retry += 1
            try:
                resp = yield from aiohttp.request(
                    'get', url, params=self.params, connector=self.connector)
                return (yield from self.handle_response(resp))
            except Exception as exc:
                sys.stderr.write('{0} has error {1}\n'.format(url, repr(exc)))
                if retry >= self.max_retries:
                    return
                sys.stderr.write(
                    '... retry {0}/{1} {2}\n'.format(retry, self.max_retries, url))
                yield from asyncio.sleep(1)

    def make_url(self, path):
        if self.hosts:
            host = self.hosts[random.randrange(len(self.hosts))]
        else:
            host = 'archive.org'
        return self.protocol + host + path


def mine(identifiers, **kwargs):
    """Concurrently retrieve metadata from Archive.org items.

    Args:
        identifiers: An iterable yielding Archive.org item identifiers.
        response_callback: A callback function to call on each
            aiohttp.client.ClientResponse object successfully returned.
        max_tasks: The maximum number of tasks to run concurrently.
        cache: A boolean indicating if the item metadata should be cached on
            Archive.org servers.
        max_retries: The maximum number of times to retry a given request.
        secure: A boolean indicating if a secure connection should be used or not.
        hosts: A list of hosts to cycle through randomly for each request.
    """
    loop = asyncio.get_event_loop()
    miner = Miner(identifiers, loop, **kwargs)
    asyncio.Task(miner.run())

    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
    except RuntimeError:
        pass

    loop.run_forever()


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

    m = mine(args.itemlist,
             max_tasks=args.workers,
             cache=args.cache,
             retries=args.retries,
             secure=args.secure,
             hosts=hosts
        )


if __name__ == '__main__':
    main()
