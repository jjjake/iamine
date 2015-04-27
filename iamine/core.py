import urllib.request
try:
    import ujson as json
except ImportError:
    import json
import asyncio
from copy import deepcopy
import time

import aiohttp

from .config import get_config
from .requests import MineRequest
from .urls import metadata_urls, make_url


class Miner(object):

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

        self.cookies = config.get('cookies', {})
        self.connector = aiohttp.TCPConnector(share_cookies=True, loop=loop)
        self.connector.update_cookies(self.cookies)

        # Asyncio/Aiohttp settings.
        self.tasks = set()
        self.loop = loop
        self.sem = asyncio.Semaphore(max_tasks)

        # Rate limiting.
        self._max_per_second = self.get_global_rate_limit()
        self._min_interval = 1.0 / float(self._max_per_second)
        self._last_time_called = 0.0

    def get_global_rate_limit(self):
        """Get the global rate limit per client.

        :rtype: int
        :returns: The global rate limit for each client.
        """
        r = urllib.request.urlopen('https://archive.org/metadata/iamine-rate-limiter')
        j = json.loads(r.read().decode('utf-8'))
        return int(j.get('metadata', {}).get('rate_per_second', 300))

    @asyncio.coroutine
    def mine_urls(self, urls, params=None, callback=None):
        def _md_request_generator():
            for url in urls:
                resp = MineRequest('GET', url,
                           callback=callback,
                           max_retries=self.max_retries,
                           debug=self.debug,
                           params=params,
                           connector=self.connector
                       )
                yield resp

        task = asyncio.Task(self.add_requests(_md_request_generator()))
        task.add_done_callback(self.tasks.remove)
        self.tasks.add(task)

        # Sleep until all tasks are complete.
        while self.tasks:
            yield from asyncio.sleep(.1)

    @asyncio.coroutine
    def add_requests(self, requests):
        for request in requests:
            yield from self.sem.acquire()
            task = asyncio.Task(self.make_rate_limited_request(request))
            task.add_done_callback(lambda t: self.sem.release())
            task.add_done_callback(self.tasks.remove)
            self.tasks.add(task)

    def _rate_limited():
        """A rate limit decorator for limiting the number of times the
        decorated :class:`Miner` method can be called. Limits are set in
        :attr:`Miner._max_per_second`.
        """
        def decorate(func):
            def rate_limited_func(self, *args, **kwargs):
                elapsed = time.monotonic() - self._last_time_called
                self.left_to_wait = self._min_interval - elapsed
                if self.left_to_wait > 0:
                    time.sleep(self.left_to_wait)
                func(self, *args, **kwargs)
                self._last_time_called = time.monotonic()
                yield from func(self, *args, **kwargs)
            return rate_limited_func
        return decorate

    @_rate_limited()
    def make_rate_limited_request(self, request):
        yield from request.make_request()


class ItemMiner(Miner):

    def __init__(self, **kwargs):
        super(ItemMiner, self).__init__(**kwargs)

    @asyncio.coroutine
    def mine_items(self, identifiers, params=None, callback=None):
        """Mine metadata from Archive.org items.

        :param identifiers: Archive.org identifiers to be mined.
        :type identifiers: iterable

        :param params: URL parameters to send with each metadata
                       request.
        :type params: dict

        :param callback: A callback function to be called on each
                         :py:class:`aiohttp.client.ClientResponse`.
        :type callback: func
        """
        # By default, don't cache item metadata in redis.
        params = {'dontcache': 1} if not params else {}
        urls = metadata_urls(identifiers, self.protocol, self.hosts)
        yield from self.mine_urls(urls, params, callback)


class SearchMiner(ItemMiner):

    def __init__(self, **kwargs):
        super(SearchMiner, self).__init__(**kwargs)

    @asyncio.coroutine
    def search(self, query=None, params=None, callback=None, mine_ids=None):
        """Mine Archive.org search results.

        :param query: The Archive.org search query to yield results for.
                      Refer to https://archive.org/advancedsearch.php#raw
                      for help formatting your query.
        :type query: str

        :param params: The URL parameters to send with each request sent
                       to the Archive.org Advancedsearch Api.
        :type params: dict
        """
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
        url = make_url('/advancedsearch.php', self.protocol, self.hosts)

        search_info = yield from self.get_search_info(search_params)
        total_results = search_info.get('response', {}).get('numFound', 0)
        total_pages = (int(total_results/search_params['rows']) + 1)

        requests = []
        for page in range(1, (total_pages + 2)):
            params = deepcopy(search_params)
            params['page'] = page
            if not callback and mine_ids:
                callback = self._handle_search_results
            request = MineRequest('GET', url,
                          callback=callback,
                          max_retries=self.max_retries,
                          params=params
                      )
            requests.append(request)
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

    def get_search_info(self, params):
        url = make_url('/advancedsearch.php?', self.protocol, self.hosts)
        p = deepcopy(params)
        p['rows'] = 0
        resp = yield from aiohttp.request('get', url, params=p)
        resp.close()
        j = yield from resp.json(encoding='utf-8')
        return {} if not j else j

    @asyncio.coroutine
    def _handle_search_results(self, resp, mine_ids=None, params=None, callback=None):
        j = yield from resp.json(encoding='utf-8')
        resp.close()
        identifiers = []
        for doc in j.get('response', {}).get('docs', []):
            if not doc.get('identifier'):
                continue
            identifiers.append(doc['identifier'])
        task = asyncio.Task(self.mine_items(identifiers, params, callback))
        task.add_done_callback(self.tasks.remove)
        self.tasks.add(task)
