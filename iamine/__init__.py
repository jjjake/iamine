#!/usr/bin/env python3
import argparse
import logging
import signal
import os
import sys
import asyncio

import aiohttp


class Crawler:

    def __init__(self, identifiers, loop, done_callback=None, maxtasks=None):
        maxtasks = 100 if not maxtasks else maxtasks

        self.identifiers = identifiers
        self.loop = loop
        self.todo = set()
        self.busy = set()
        self.tasks = set()
        self.done_callback = done_callback
        self.sem = asyncio.Semaphore(maxtasks)

        # connector stores cookies between requests and uses connection pool
        self.connector = aiohttp.TCPConnector(share_cookies=True, loop=loop)

    @asyncio.coroutine
    def run(self):
        asyncio.Task(self.addurls(self.identifiers))  # Set initial work.
        yield from asyncio.sleep(1)
        while self.busy:
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
            url = 'http://archive.org/metadata/{}'.format(identifier.strip())
            self.todo.add(url)
            yield from self.sem.acquire()
            task = asyncio.Task(self.process(url))
            task.add_done_callback(lambda t: self.sem.release())
            task.add_done_callback(self.tasks.remove)
            task.add_done_callback(self._done_callback)
            self.tasks.add(task)

    @asyncio.coroutine
    def process(self, url):
        self.todo.remove(url)
        self.busy.add(url)
        resp = None
        data = None
        i = 0
        max_retries = 10
        while True:
            i += 1
            try:
                resp = yield from aiohttp.request(
                    'get', url, connector=self.connector)
                break
            except Exception as exc:
                sys.stderr.write('{0} has error {1}\n'.format(url, repr(exc)))
                if i >= max_retries:
                    break
                sys.stderr.write('... retry {0}/{1} {2}\n'.format(i, max_retries, url))
                yield from asyncio.sleep(1)

        if resp:
            yield from resp.read()
            resp.close()
        self.busy.remove(url)
        return resp


def main():
    parser = argparse.ArgumentParser(description='''Concurrently retrieve metadata from
                                                    Archive.org items.''')

    parser.add_argument('itemlist', nargs='?', default=sys.stdin, 
                        help='''A file containing Archive.org identifiers, one per line,
                                for which to retrieve metadata from. If no itemlist is
                                provided, identifiers will be read from stdin.''')
    parser.add_argument('--workers', type=int, 
                        help='The maximum number of tasks to run at once.')
    args = parser.parse_args()

    if args.itemlist is sys.stdin:
        if not (os.fstat(sys.stdin.fileno()).st_size > 0):
            # Exit with 2 if stdin appears to be empty.
            sys.exit(2)

    loop = asyncio.get_event_loop()
    
    if not hasattr(args.itemlist, 'read'):
        itemlist = open(args.itemlist)
    else:
        itemlist = args.itemlist

    c = Crawler(itemlist, loop, maxtasks=args.workers)
    asyncio.Task(c.run())

    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
    except RuntimeError:
        pass

    loop.run_forever()


if __name__ == '__main__':
    main()
