import signal
import asyncio
import urllib.parse
import urllib.request
import json

from .core import Miner


def search(query=None, params=None, callback=None, mine_ids=None, info_only=None,
           **kwargs):
    query = '(*:*)' if not query else query
    params = params if params else {}
    mine_ids = True if mine_ids else False
    info_only = True if info_only else info_only

    if not kwargs.get('loop'):
        loop = asyncio.get_event_loop()
    else:
        loop = kwargs['loop']
    miner = Miner(loop, **kwargs)

    if info_only:
        url = miner.make_url('/advancedsearch.php?')
        params = urllib.parse.urlencode(miner.get_search_params(query, params))
        resp = urllib.request.urlopen(url + params)
        j = json.loads(resp.read().decode('utf-8'))
        search_info = j['responseHeader']
        search_info['numFound'] = j.get('response', {}).get('numFound', 0)
        return search_info

    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        loop.run_until_complete(miner.search(query, params=params, callback=callback,
                                             mine_ids=mine_ids))
    except RuntimeError:
        pass


def mine_items(identifiers, params=None, callback=None, **kwargs):
    """Concurrently retrieve metadata from Archive.org items.

    Args:
        identifiers: An iterable yielding Archive.org item identifiers.
        response_callback: A callback function to call on each
            aiohttp.client.ClientResponse object successfully returned.
        max_tasks: The maximum number of tasks to run concurrently.
        max_retries: The maximum number of times to retry a given request.
        secure: A boolean indicating if a secure connection should be used or not.
        hosts: A list of hosts to cycle through randomly for each request.
    """
    if not kwargs.get('loop'):
        loop = asyncio.get_event_loop()
    else:
        loop = kwargs['loop']
    miner = Miner(loop, **kwargs)
    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        loop.run_until_complete(miner.mine_items(identifiers, callback))
    except RuntimeError:
        pass
