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
