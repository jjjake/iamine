import asyncio
import functools
from copy import deepcopy
import sys
import random

import aiohttp


class Miner:

    def __init__(self, loop=None, max_tasks=None, retries=None, secure=None, hosts=None,
                 params=None):
        # Set default values for kwargs.
        max_tasks = 100 if not max_tasks else max_tasks
        max_retries = 10 if not retries else retries
        protocol = 'http://' if not secure else 'https://'
        loop = asyncio.get_event_loop() if not loop else loop

        self.protocol = protocol
        self.hosts = hosts
        self.max_retries = max_retries

        # Asyncio/Aiohttp settings.
        self.tasks = set()
        self.loop = loop
        self.sem = asyncio.Semaphore(max_tasks)
        self.connector = aiohttp.TCPConnector(share_cookies=True, loop=loop)

    @asyncio.coroutine
    def mine_items(self, identifiers, params=None, callback=None):
        callback = functools.partial(self.handle_response, callback=callback)
        # By default, don't cache item metadata in redis.
        params = {'dontcache': 1} if not params else {}

        def _md_request_generator():
            for identifier in identifiers:
                url = self.make_url('/metadata/{}'.format(identifier))
                yield (url, params, callback)

        task = asyncio.Task(self.add_requests(_md_request_generator()))
        task.add_done_callback(self.tasks.remove)
        self.tasks.add(task)

        # Sleep until all tasks are complete.
        while self.tasks:
            yield from asyncio.sleep(.1)

    @asyncio.coroutine
    def handle_response(self, resp, callback=None):
        if callback:
            yield from callback(resp)
            resp.close()
        else:
            content = yield from resp.read()
            resp.close()
            print(content.decode('utf-8'))

    @asyncio.coroutine
    def search(self, query=None, params=None, callback=None, mine_ids=None):
        search_params = self.get_search_params(query, params)
        url = self.make_url(path='/advancedsearch.php')

        search_info = yield from self.get_search_info(url, search_params)
        total_results = search_info.get('response', {}).get('numFound', 0)
        total_pages = (int(total_results/search_params['rows']))

        for page in range(1, (total_pages + 2)):
            params = deepcopy(search_params)
            params['page'] = page
            cb = functools.partial(self._handle_search_results, callback=callback,
                                   mine_ids=mine_ids)
            task = asyncio.Task(self.add_requests([(url, params, cb)]))
            task.add_done_callback(self.tasks.remove)
            self.tasks.add(task)

        # Sleep until all tasks are complete.
        while self.tasks:
            yield from asyncio.sleep(.1)

    def get_search_params(self, query, params):
        default_rows = 1000
        search_params = {
            'q': '(*:*)',
            'fl[]': 'identifier',
            'page': 1,
            'output': 'json',
        }
        if params:
            search_params.update({k: v for k, v in params.items() if v})
        if query:
            search_params['q'] = query
        if 'rows' not in search_params:
            search_params['rows'] = default_rows
        return search_params

    def get_search_info(self, url, params):
        p = deepcopy(params)
        p['rows'] = 0
        resp = yield from aiohttp.request('get', url, params=p)
        resp.close()
        return (yield from resp.json(encoding='utf-8'))

    @asyncio.coroutine
    def _handle_search_results(self, resp, mine_ids=None, params=None, callback=None):
        params = {'dontcache': 1} if not params else params
        callback = functools.partial(self.handle_response, callback=callback)

        if not mine_ids:
            task = asyncio.Task(self.handle_response(resp, callback=callback))
            task.add_done_callback(self.tasks.remove)
            self.tasks.add(task)
        else:
            j = yield from resp.json(encoding='utf-8')
            resp.close()
            requests = []
            for doc in j.get('response', {}).get('docs', []):
                url = self.make_url('/metadata/{}'.format(doc['identifier']))
                requests.append((url, params, callback))
            if requests:
                task = asyncio.Task(self.add_requests(requests))
                task.add_done_callback(self.tasks.remove)
                self.tasks.add(task)

    @asyncio.coroutine
    def add_requests(self, requests):
        for url, params, callback in requests:
            yield from self.sem.acquire()
            task = asyncio.Task(self.make_request(url, params, callback))
            task.add_done_callback(lambda t: self.sem.release())
            task.add_done_callback(self.tasks.remove)
            self.tasks.add(task)

    @asyncio.coroutine
    def make_request(self, url, params=None, callback=None):
        params = {'dontcache': 1} if not params else params
        retry = 0
        while True:
            retry += 1
            try:
                resp = yield from aiohttp.request(
                    'get', url, params=params, connector=self.connector)
                if callback:
                    return (yield from callback(resp))
                else:
                    return resp
            except Exception as exc:
                raise exc
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
