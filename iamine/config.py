import os.path
import configparser
import json
import asyncio

import aiohttp

from .exceptions import AuthenticationError


@asyncio.coroutine
def _get_auth_config(username, password):
    conn = aiohttp.connector.TCPConnector(share_cookies=True)

    # Login POST data.
    data = dict(
        # Cookies will expire very quickly without remember=CHECKED.
        remember='CHECKED',
        action='login',
        username=username,
        password=password,
    )

    # Login to Archive.org and add logged-in cookies to connector.
    r = yield from aiohttp.request(
            method='POST',
            url='https://archive.org/account/login.php',
            auth=aiohttp.helpers.BasicAuth(login=username, password=password),
            data=data,
            headers={'Cookie': 'test-cookie=1'},
            connector=conn)
    r.close()

    # Archive.org returns 200 for failed authentication,
    # detect auth failure by some other means.
    if 'logged-in-user' not in conn.cookies:
        raise AuthenticationError(
            'Failed to authenticate. Please check your credentials and try again.')

    # Get S3 keys using the cookies attached to the connector
    r = yield from aiohttp.request(
            method='GET',
            url='https://archive.org/account/s3.php',
            params=dict(output_json=1),
            connector=conn)
    r.close()
    j = json.loads((yield from r.read()).decode('utf-8'))

    auth_config = {
        's3': {
            'access': j.get('key', {}).get('s3accesskey'),
            'secret': j.get('key', {}).get('s3secretkey'),
        },
        'cookies': {
            'logged-in-user': conn.cookies.get('logged-in-user').value,
            'logged-in-sig': conn.cookies.get('logged-in-sig').value,
        }
    }
    conn.close()
    return auth_config


def get_auth_config(username, password):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_get_auth_config(username, password))


def get_config_file(config_file=None):
    config = configparser.RawConfigParser()

    if not config_file:
        config_dir = os.path.expanduser('~/.config/')
        if not os.path.isdir(config_dir):
            config_file = os.path.expanduser('~/.ia')
        else:
            config_file = '{0}/ia.ini'.format(config_dir)
    config.read(config_file)

    return (config_file, config)


def write_config_file(username, password, overwrite=None, config_file=None):
    config_file, config = get_config_file(config_file)
    auth_config = get_auth_config(username, password)

    # S3 Keys.
    if ('s3' in config) and (not overwrite):
        config_access = config.get('s3', 'access', fallback=None)
        if not config_access:
            config['s3']['access'] = auth_config.get('s3', {}).get('access')
        config_secret = config.get('s3', 'secret', fallback=None)
        if not config_secret:
            config['s3']['secret'] = auth_config.get('s3', {}).get('secret')
    else:
        config['s3'] = auth_config.get('s3')

    # Cookies.
    cookies = auth_config.get('cookies', {})
    if ('cookies' in config) and (not overwrite):
        config_user = config.get('cookies', 'logged-in-user', fallback=None)
        if not config_user:
            config['cookies']['logged-in-user'] = cookies.get('logged-in-user')
        config_sig = config.get('cookies', 'logged-in-sig', fallback=None)
        if not config_sig:
            config['cookies']['logged-in-sig'] = cookies.get('logged-in-sig')
    else:
        config['cookies'] = cookies

    # Write config file.
    with open(config_file, 'w') as fh:
        os.chmod(config_file, 0o700)
        config.write(fh)

    return config_file


def get_config(config=None, config_file=None):
    _config = {} if not config else config
    config_file, config = get_config_file(config_file)
    if not os.path.isfile(config_file):
        return _config

    config_dict = {
        's3': {
            'access': config.get('s3', 'access', fallback=None),
            'secret': config.get('s3', 'secret', fallback=None),
        },
        'cookies': {
            'logged-in-user': config.get('cookies', 'logged-in-user', fallback=None),
            'logged-in-sig': config.get('cookies', 'logged-in-sig', fallback=None),
        },
    }

    return dict((k, v) for k, v in config_dict.items() if v)
