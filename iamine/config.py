import os.path
import configparser
import urllib.parse
import urllib.request
import http.cookiejar
import json

from .exceptions import AuthenticationException


def get_auth_config(username, password):
    cj = http.cookiejar.CookieJar()

    # Get logged-in cookies.
    url = 'https://archive.org/account/login.php'
    data = ('remember=CHECKED&action=login&'
            'username={0}&password={1}'.format(username, password))
    encoded_data = data.encode('utf-8')
    headers = {'Cookie': 'test-cookie="1"'}

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(url, data=encoded_data, headers=headers)
    opener.open(req)

    # Get S3 keys.
    url = 'https://archive.org/account/s3.php?output_json=1'
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    r = opener.open(url)
    j = json.loads(r.read().decode('utf-8'))

    if not j.get('success'):
        raise AuthenticationException(
            'Failed to authenticate. Please check your credentials and try again.')

    # Parse S3 keys and cookies to auth_config.
    s3_keys = {
        'access': j.get('key', {}).get('s3accesskey'),
        'secret': j.get('key', {}).get('s3secretkey'),
    }

    cookies = {}
    ia_cookies = cj._cookies.get('.archive.org', {}).get('/')
    for c in ia_cookies:
        if 'logged-in-' in c:
            cookies[c] = ia_cookies[c].value

    auth_config = {
        's3': s3_keys,
        'cookies': cookies,
    }
    return auth_config


def get_config_file():
    config = configparser.ConfigParser()

    config_dir = os.path.expanduser('~/.config/')
    if not os.path.isdir(config_dir):
        config_file = os.path.expanduser('~/.ia')
    else:
        config_file = '{0}/ia.ini'.format(config_dir)
    config.read(config_file)

    return (config_file, config)


def write_config_file(username, password, overwrite=None):
    config_file, config = get_config_file()
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
    cookies = dict((k, v.replace('%', '%%')) for k, v in cookies.items())
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


def get_config(config=None):
    _config = {} if not config else config
    config_file, config = get_config_file()
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
