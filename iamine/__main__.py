#!/usr/bin/env python3
"""Concurrently retrieve metadata from Archive.org items.

usage: ia-mine [--config-file=<FILE>] (<itemlist> | -) [--debug] [--workers WORKERS] [--cache]
               [--retries RETRIES] [--secure] [--hosts HOSTS]
       ia-mine [--all | --search QUERY] [[--info | --info --field FIELD...]
               |--num-found | --mine-ids | --field FIELD... | --itemlist]
               [--debug] [--rows ROWS] [--workers WORKERS] [--cache]
               [--retries RETRIES] [--secure] [--hosts HOSTS]
       ia-mine [--config-file=<FILE>] [-h | --version | --configure]

positional arguments:
  itemlist              A file containing Archive.org identifiers, one per
                        line, for which to retrieve metadata from. If no
                        itemlist is provided, identifiers will be read from
                        stdin.

optional arguments:
  -h, --help                 Show this help message and exit.
  -v, --version              Show program's version number and exit.
  --configure                Configure ia-mine to use your Archive.org credentials.
  -C, --config-file=<FILE>   The config file to use.
  -d, --debug                Turn on verbose logging [default: False]
  -a, --all                  Mine all indexed items.
  -s, --search QUERY         Mine search results. For help formatting your query,
                             see: https://archive.org/advancedsearch.php
  -m, --mine-ids             Mine items returned from search results.
                             [default: False]
  -i, --info                 Print search result response header to stdout and exit.
  -f, --field FIELD          Fields to include in search results.
  -i, --itemlist             Print identifiers only to stdout. [default: False]
  -n, --num-found            Print the number of items found for the given search
                             query.
  --rows ROWS                The number of rows to return for each request made to
                             the Archive.org Advancedsearch API. On slower networks,
                             it may be useful to use a lower value, and on faster
                             networks, a higher value. [default: 50]
  -w, --workers WORKERS
                             The maximum number of tasks to run at once.
                             [default: 100]
  -c, --cache                Cache item metadata on Archive.org. Items are not
                             cached are not cached by default.
  -r, --retries RETRIES
                             The maximum number of retries for each item.
                             [default: 10]
  --secure                   Use HTTPS. HTTP is used by default.
  -H, --hosts HOSTS          A file containing a list of hosts to shuffle through.

"""
from .utils import suppress_interrupt_messages, suppress_brokenpipe_messages, handle_cli_exceptions
suppress_interrupt_messages()
suppress_brokenpipe_messages()
handle_cli_exceptions()

import logging
import os
import sys
import json

from docopt import docopt, DocoptExit
from schema import Schema, Use, Or, SchemaError

from .api import mine_items, search, configure
from . import __version__
from .exceptions import AuthenticationError


asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.setLevel(logging.CRITICAL)


def print_itemlist(resp):
    j = yield from resp.json(encoding='utf-8')
    for doc in j.get('response', {}).get('docs', []):
        print(doc.get('identifier'))


def main(argv=None, session=None):
    # If ia-wrapper calls main with argv argument, strip the
    # "mine" subcommand from args.
    argv = argv[1:] if argv else sys.argv[1:]

    # Catch DocoptExit error and write to stderr manually.
    # Otherwise error's vanish if executed from a pex binary.
    try:
        args = docopt(__doc__, version=__version__, argv=argv, help=True)
    except DocoptExit as exc:
        sys.exit(sys.stderr.write('{}\n'.format(exc.code)))

    # Validate args.
    open_file_or_stdin = lambda f: sys.stdin if (f == '-') or (not f) else open(f)
    parse_hosts = lambda f: [x.strip() for x in open(f) if x.strip()]
    schema = Schema({object: bool,
        '--search': Or(None, Use(str)),
        '--field': list,
        '--config-file': Or(None, str),
        '--rows': Use(int,
            error='"{}" should be an integer'.format(args['--rows'])),
        '--hosts': Or(None, Use(parse_hosts,
            error='"{}" should be a readable file.'.format(args['--hosts']))),
        '--retries': Use(int, '"{}" should be an integer.'.format(args['--retries'])),
        '<itemlist>': Use(open_file_or_stdin,
            error='"{}" should be readable'.format(args['<itemlist>'])),
        '--workers': Use(int,
            error='"{}" should be an integer.'.format(args['--workers'])),
    })
    try:
        args = schema.validate(args)
    except SchemaError as exc:
        sys.exit(sys.stderr.write('error: {1}\n{0}'.format(__doc__, str(exc))))

    # Configure.
    if args['--configure']:
        sys.stdout.write(
            'Enter your Archive.org credentials below to configure ia-mine.\n\n')
        try:
            configure(overwrite=True, config_file=args['--config-file'])
        except AuthenticationError as exc:
            sys.stdout.write('\n')
            sys.stderr.write('error: {}\n'.format(str(exc)))
            sys.exit(1)
        sys.exit(0)

    # Search.
    if args['--search'] or args['--all']:
        query = 'all:1' if not args['--search'] else args['--search']
        callback = print_itemlist if args['--itemlist'] else None
        info_only = True if args['--info'] or args['--num-found'] else False
        params = {
            'rows': args['--rows']
        }
        for i, f in enumerate(args['--field']):
            params['fl[{}]'.format(i)] = f
        r = search(query,
                params=params,
                callback=callback,
                mine_ids=args['--mine-ids'],
                info_only=info_only,
                max_tasks=args['--workers'],
                retries=args['--retries'],
                config_file=args['--config-file'],
                secure=args['--secure'],
                hosts=args['--hosts'],
                debug=args['--debug'])
        if args['--info']:
            sys.stdout.write('{}\n'.format(json.dumps(r)))
        elif args['--num-found']:
            sys.stdout.write('{}\n'.format(r.get('numFound', 0)))
        sys.exit(0)

    # Mine.
    else:
        # Exit with 2 if stdin appears to be empty.
        if args['-']:
            if (not os.fstat(sys.stdin.fileno()).st_size > 0) and (sys.stdin.seekable()):
                sys.exit(2)

        mine_items(args['<itemlist>'],
                   max_tasks=args['--workers'],
                   retries=args['--retries'],
                   secure=args['--secure'],
                   hosts=args['--hosts'],
                   config_file=args['--config-file'],
                   debug=args['--debug'])


if __name__ == '__main__':
    main()
