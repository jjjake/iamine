import os
import locale
import sys
import asyncio
try:
    import ujson as json
except ImportError:
    import json
import traceback

import aiohttp

from . import __version__


class MineRequest(object):

    def __init__(self, method, url, access_key, *,
                 callback=None,
                 max_retries=None,
                 debug=None,
                 **kwargs):

        max_retries = 10 if not max_retries else max_retries

        self.method = method
        self.url = url
        self.callback = callback
        self.max_retries = max_retries
        self.debug = debug
        self.request_kwargs = kwargs
        self.access_key = access_key

        self._headers = kwargs.get('headers', {})
        self._user_agent = self._get_user_agent_string()

    @property
    def headers(self):
        headers = dict((k, v) for k, v in self._headers if k.lower() != 'user-agent')
        headers['User-agent'] = self._user_agent
        return headers

    def _get_user_agent_string(self):
        uname = os.uname()
        try:
            lang = locale.getlocale()[0][:2]
        except:
            lang = ''
        py_version = '{0}.{1}.{2}'.format(*sys.version_info)
        return 'ia-mine/{0} ({1} {2}; N; {3}; {4}) Python/{5}'.format(
            __version__, uname.sysname, uname.machine, lang, self.access_key, py_version)

    def _handle_response(self, resp):
        if self.callback:
            yield from self.callback(resp)
            resp.close()
        else:
            j = yield from resp.json()
            resp.close()
            print(json.dumps(j))

    @asyncio.coroutine
    def make_request(self):
        retries = 0
        while retries < self.max_retries:
            try:
                resp = yield from aiohttp.request(self.method, self.url,
                                                  **self.request_kwargs)
                return (yield from self._handle_response(resp))
            except Exception as exc:
                retries += 1
                error = dict(
                    url=self.url,
                    params=self.request_kwargs.get('params'),
                    message='Request failed, retrying.',
                    retries_left=self.max_retries-retries,
                )
                if self.debug:
                    error['callback'] = repr(self.callback)
                    error['exception'] = repr(exc)
                    error['traceback'] = traceback.format_exc()
                    sys.stderr.write('{}\n'.format(json.dumps(error)))
            yield from asyncio.sleep(1)
        else:
            error['message'] = 'Maximum retries exceeded for url, giving up.'
            sys.stderr.write('{}\n'.format(json.dumps(error)))
            return
