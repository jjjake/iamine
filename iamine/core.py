import os
import sys
import locale
import urllib.parse
import asyncio
import functools
from copy import deepcopy
import random
try:
    import ujson as json
except ImportError:
    import json

import aiohttp

from ._version import __version__
from .config import get_config


class Miner:

    def __init__(self, loop=None, max_tasks=None, retries=None, secure=None, hosts=None,
                 params=None, config=None, debug=None):
        # Set default values for kwargs.
        loop = asyncio.get_event_loop() if not loop else loop
        max_tasks = 100 if not max_tasks else max_tasks
        max_retries = 10 if not retries else retries
        protocol = 'http://' if not secure else 'https://'
        config = get_config(config)
        debug = True if debug else False

        self.max_retries = max_retries
        self.protocol = protocol
        self.hosts = hosts
        self.config = config
        self.debug = debug
        self.cookies = config.get('cookies')

        # Set User-agent.
        uname = os.uname()
        lang = locale.getlocale()[0][:2]
        py_version = '{0}.{1}.{2}'.format(*sys.version_info)
        user = urllib.parse.unquote(config.get('cookies', {}).get('logged-in-user', ''))
        ua = 'ia-mine/{0} ({1} {2}; N; {3}; {4}) Python/{5}'.format(
            __version__, uname.sysname, uname.machine, lang, user, py_version)
        self.headers = {'User-agent': ua}

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
        # When mining id's, the only field we need returned is "identifier".
        if mine_ids and params:
            params = dict((k, v) for k, v in params.items() if 'fl' not in k)
            params['fl[]'] = 'identifier'

        # Make sure "identifier" is always returned in search results.
        fields = [k for k in params if 'fl' in k]
        if (len(fields) == 1) and (not any('identifier' == params[k] for k in params)):
            # Make sure to not overwrite the existing fl[] key.
            i = 0
            while params.get('fl[{}]'.format(i)):
                i += 1
            params['fl[{}]'.format(i)] = 'identifier'

        search_params = self.get_search_params(query, params)
        # If returning entire index and sort parameter is not set,
        # sort by most downloaded.
        if search_params['q'] == "(*:*)" and not any('sort' in k for k in search_params):
            search_params['sort[]'] = 'downloads desc'

        url = self.make_url(path='/advancedsearch.php')

        search_info = yield from self.get_search_info(url, search_params)
        total_results = search_info.get('response', {}).get('numFound', 0)
        total_pages = (int(total_results/search_params['rows']) + 1)

        requests = []
        for page in range(1, (total_pages + 2)):
            params = deepcopy(search_params)
            params['page'] = page
            cb = functools.partial(self._handle_search_results, callback=callback,
                                   mine_ids=mine_ids)
            requests.append((url, params, cb))
            # Submit 5 tasks at a time.
            if (page % 5 == 0) or (page == total_pages):
                task = asyncio.Task(self.add_requests(requests))
                task.add_done_callback(self.tasks.remove)
                self.tasks.add(task)
                yield from asyncio.sleep(.01)
                requests = []

        # Sleep until all tasks are complete.
        while self.tasks:
            yield from asyncio.sleep(.1)

    def get_search_params(self, query, params):
        default_rows = 1000
        search_params = {
            'q': '(*:*)',
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
        j = yield from resp.json(encoding='utf-8')
        return {} if not j else j

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
                resp = yield from aiohttp.request('get', url, params=params,
                                                  headers=self.headers,
                                                  cookies=self.cookies,
                                                  connector=self.connector)
                if callback:
                    return (yield from callback(resp))
                else:
                    return resp
            except Exception as exc:
                error = {
                    'url': url,
                    'params': params,
                    'error': exc.__doc__,
                }
                if self.debug:
                    error['callback'] = repr(callback)
                    error['exception'] = repr(exc)
                    error['retries_left'] = self.max_retries - retry
                    sys.stderr.write('{}\n'.format(json.dumps(error)))
                elif retry >= self.max_retries:
                    error['error'] = 'Maximum retries exceeded for url, giving up.'
                    sys.stderr.write('{}\n'.format(json.dumps(error)))
                    return
                yield from asyncio.sleep(1)

    def make_url(self, path):
        if self.hosts:
            host = self.hosts[random.randrange(len(self.hosts))]
        else:
            host = 'archive.org'
        return self.protocol + host + path.strip()
