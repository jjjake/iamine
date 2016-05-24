import urllib.request
try:
    import ujson as json
except ImportError:
    import json
import asyncio
try:
    from asyncio import JoinableQueue as Queue
except ImportError:
    from asyncio import Queue
from copy import deepcopy
import time

import aiohttp

from .config import get_config
from .requests import MineRequest
from .urls import metadata_urls, make_url
from .exceptions import AuthenticationError


class Miner(object):

    def __init__(self,
                 loop=None,
                 max_tasks=None,
                 retries=None,
                 secure=None,
                 hosts=None,
                 params=None,
                 config=None,
                 config_file=None,
                 access=None,
                 secret=None,
                 debug=None):

        # Set default values for kwargs.
        loop = asyncio.get_event_loop() if not loop else loop
        max_tasks = 100 if not max_tasks else max_tasks
        max_retries = 10 if not retries else retries
        protocol = 'http://' if not secure else 'https://'
        config = get_config(config, config_file)
        access = config.get('s3', {}).get('access', access)
        secret = config.get('s3', {}).get('secret', secret)
        debug = True if debug else False

        self.max_tasks = max_tasks
        self.max_retries = max_retries
        self.protocol = protocol
        self.hosts = hosts
        self.config = config
        self.access = access
        self.debug = debug
        self.cookies = config.get('cookies', {})

        # Asyncio/Aiohttp settings.
        self.connector = aiohttp.TCPConnector(share_cookies=True, loop=loop)
        self.connector.update_cookies(self.cookies)
        self.loop = loop
        self.q = Queue(1000, loop=self.loop)
        self.q = Queue(loop=self.loop)

        # Require valid access key!
        self.assert_s3_keys_valid(access, secret)

        # Rate limiting.
        self._max_per_second = self.get_global_rate_limit()
        self._min_interval = 1.0 / float(self._max_per_second)
        self._last_time_called = 0.0

    def close(self):
        self.connector.close()
        self.loop.stop()
        self.loop.close()

    def assert_s3_keys_valid(self, access, secret):
        url = '{}s3.us.archive.org?check_auth=1'.format(self.protocol)
        r = urllib.request.Request(url)
        r.add_header('Authorization', 'LOW {0}:{1}'.format(access, secret))
        f = urllib.request.urlopen(r)
        j = json.loads(f.read().decode('utf-8'))
        if j.get('authorized') is not True:
            raise AuthenticationError(j.get('error'))

    def get_global_rate_limit(self):
        """Get the global rate limit per client.

        :rtype: int
        :returns: The global rate limit for each client.
        """
        r = urllib.request.urlopen('https://archive.org/metadata/iamine-rate-limiter')
        j = json.loads(r.read().decode('utf-8'))
        return int(j.get('metadata', {}).get('rate_per_second', 300))

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

    @asyncio.coroutine
    def work(self):
        while True:
            request = yield from self.q.get()
            yield from self.make_rate_limited_request(request)
            self.q.task_done()

    @asyncio.coroutine
    def q_requests(self, requests):
        for req in requests:
            self.q.put_nowait(req)

    @asyncio.coroutine
    def mine(self, requests):
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        yield from self.q_requests(requests)

        yield from self.q.join()
        yield from asyncio.sleep(1)
        while not self.q.empty():
            yield from asyncio.sleep(1)

        for w in workers:
            w.cancel()
        yield from asyncio.sleep(.5)


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
        requests = metadata_requests(identifiers, params, callback, self)
        yield from self.mine(requests)


class SearchMiner(ItemMiner):

    def __init__(self, **kwargs):
        super(SearchMiner, self).__init__(**kwargs)
        # Item mining queue.
        self.iq = Queue(1000, loop=self.loop)

    def get_search_params(self, query, params):
        default_rows = 500
        search_params = {
            'q': 'all:1',
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

        params = urllib.parse.urlencode(p)
        url += params
        f = urllib.request.urlopen(url)
        return json.loads(f.read().decode('utf-8'))

    @asyncio.coroutine
    def _handle_search_results(self, resp, params=None, callback=None):
        j = yield from resp.json(encoding='utf-8')
        resp.close()
        identifiers = []
        for doc in j.get('response', {}).get('docs', []):
            if not doc.get('identifier'):
                continue
            identifiers.append(doc['identifier'])
        for req in metadata_requests(identifiers, params, callback, self):
            self.iq.put_nowait(req)

    def search_requests(self, query=None, params=None, callback=None, mine_ids=None):
        """Mine Archive.org search results.

        :param query: The Archive.org search query to yield results for.
                      Refer to https://archive.org/advancedsearch.php#raw
                      for help formatting your query.
        :type query: str

        :param params: The URL parameters to send with each request sent
                       to the Archive.org Advancedsearch Api.
        :type params: dict
        """
        # If mining ids, devote half the workers to search and half to item mining.
        if mine_ids:
            self.max_tasks = self.max_tasks/2
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

        search_info = self.get_search_info(search_params)
        total_results = search_info.get('response', {}).get('numFound', 0)
        total_pages = (int(total_results/search_params['rows']) + 1)

        for page in range(1, (total_pages + 1)):
            params = deepcopy(search_params)
            params['page'] = page
            if not callback and mine_ids:
                callback = self._handle_search_results
            req = MineRequest('GET', url, self.access,
                              callback=callback,
                              max_retries=self.max_retries,
                              debug=self.debug,
                              params=params,
                              connector=self.connector)
            yield req

    @asyncio.coroutine
    def mine_items(self):
        while True:
            request = yield from self.iq.get()
            yield from self.make_rate_limited_request(request)
            self.iq.task_done()

    @asyncio.coroutine
    def search(self, query=None, params=None, callback=None, mine_ids=None):
        search_requests = self.search_requests(query, params, callback, mine_ids)
        if mine_ids:
            workers = [asyncio.Task(self.mine_items(), loop=self.loop)
                       for _ in range(self.max_tasks)]

        yield from self.mine(search_requests)
        # Wait a bit for all connections to close.
        yield from asyncio.sleep(1)

        if mine_ids:
            for w in workers:
                w.cancel()


# metadata_requests() ____________________________________________________________________
def metadata_requests(identifiers, params=None, callback=None, miner=None):
    protocol = None if not miner else miner.protocol
    hosts = None if not miner else miner.hosts
    urls = metadata_urls(identifiers, protocol, hosts)

    for url in urls:
        yield MineRequest('GET', url, miner.access,
                          callback=callback,
                          max_retries=miner.max_retries,
                          debug=miner.debug,
                          params=params,
                          connector=miner.connector)
