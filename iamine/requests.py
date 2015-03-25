import os
import locale
import sys
import urllib.parse
import asyncio
import json

import aiohttp

from .config import get_config
from . import __version__


class MineRequest(object):

    def __init__(self, method, url, *, callback=None, max_retries=None, debug=None,
                 **kwargs):

        max_retries = 10 if not max_retries else max_retries
        config = get_config({})

        self.method = method
        self.url = url
        self.params = kwargs.get('params')
        self.callback = callback
        self.retries = max_retries
        self.cookies = config.get('cookies', {})
        self.debug = debug
        self.kwargs = kwargs

        # Set User-agent.
        uname = os.uname()
        try:
            lang = locale.getlocale()[0][:2]
        except:
            lang = ''
        py_version = '{0}.{1}.{2}'.format(*sys.version_info)
        user = urllib.parse.unquote(config.get('cookies', {}).get('logged-in-user', ''))
        ua = 'ia-mine/{0} ({1} {2}; N; {3}; {4}) Python/{5}'.format(
            __version__, uname.sysname, uname.machine, lang, user, py_version)
        if not self.kwargs.get('headers'):
            self.kwargs['headers'] = {}
        self.kwargs['headers']['User-agent'] = ua

    def _handle_response(self, resp):
        if self.callback:
            yield from self.callback(resp)
            resp.close()
        else:
            content = yield from resp.read()
            resp.close()
            print(content.decode('utf-8'))

    @asyncio.coroutine
    def make_request(self):
        while True:
            self.retries -= 1
            try:
                resp = yield from aiohttp.request(self.method, self.url, **self.kwargs)
                return (yield from self._handle_response(resp))
            except Exception as exc:
                raise
                error = {
                    'url': self.url,
                    'params': self.params,
                    'error': repr(exc),
                }
                if self.debug:
                    error['callback'] = repr(self.callback)
                    error['exception'] = repr(exc)
                    error['retries_left'] = self.retries
                    sys.stderr.write('{}\n'.format(json.dumps(error)))
                if self.retries <= 0:
                    error['error'] = 'Maximum retries exceeded for url, giving up.'
                    sys.stderr.write('{}\n'.format(json.dumps(error)))
                    return
                yield from asyncio.sleep(1)
