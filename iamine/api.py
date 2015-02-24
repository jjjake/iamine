import signal
import asyncio

from .core import Miner


def mine_items(identifiers, **kwargs):
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
