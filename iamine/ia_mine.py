#!/usr/bin/env python3
"""Concurrently retrieve metadata from Archive.org items.

usage: ia-mine (<itemlist> | -) [--workers WORKERS] [--cache]
               [--retries RETRIES] [--secure] [--hosts HOSTS]
       ia-mine --search QUERY [--field FIELD... | --mine-ids | --itemlist]
               [--workers WORKERS] [--cache] [--retries RETRIES]
               [--secure] [--hosts HOSTS]
       ia-mine [-h | --version] 


positional arguments:
  itemlist              A file containing Archive.org identifiers, one per
                        line, for which to retrieve metadata from. If no
                        itemlist is provided, identifiers will be read from
                        stdin.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -s, --search QUERY    mine search search results.
  -m, --mine-ids        mine items returned from search results.
                        [default: False]
  -f, --field FIELD     fields to include in search results.
                        [default: identifier]
  -i, --itemlist        dump identifiers only to stdout. [default: False]
  -w, --workers WORKERS
                        The maximum number of tasks to run at once.
                        [default: 100]
  -c, --cache           Cache item metadata on Archive.org. Items are not
                        cached are not cached by default.
  -r, --retries RETRIES
                        The maximum number of retries for each item.
                        [default: 10]
  -s, --secure          Use HTTPS. HTTP is used by default.
  -H, --hosts HOSTS     A file containing a list of hosts to shuffle through.

"""
def suppress_keyboard_interrupt_message():
    """Register a new excepthook to suppress KeyboardInterrupt
    exception messages, and exit with status code 130.

    """
    old_excepthook = sys.excepthook

    def new_hook(type, value, traceback):
        if type != KeyboardInterrupt:
            old_excepthook(type, value, traceback)
        else:
            sys.exit(130)

    sys.excepthook = new_hook

import os
import sys
suppress_keyboard_interrupt_message()

from docopt import docopt, DocoptExit
from schema import Schema, Use, Or, SchemaError

from .api import mine_items, search
from ._version import __version__


def print_itemlist(resp):
    j = yield from resp.json(encoding='utf-8')
    for doc in j.get('response', {}).get('docs', []):
        print(doc.get('identifier'))

def main(argv=None):
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
        '--hosts': Or(None, 
            Use(parse_hosts, error='--hosts=HOSTS should be a readable file.')),
        '--retries': Use(int, 'RETRIES should be an integer.'),
        '<itemlist>': Use(open_file_or_stdin, error='<itemlist> should be readable'),
        '--workers': Use(int, error='--workers=WORKERS should be an integer.'),
    })
    try:
        args = schema.validate(args)
    except SchemaError as exc:
        sys.exit(sys.stderr.write('{0}error: {1}\n'.format(__doc__, str(exc))))

    if args['--search']:
        callback = print_itemlist if args['--itemlist'] else None
        params = {}
        if 'identifier' not in args['--field']:
            args['--field'].append('identifier')
        for i, f in enumerate(args['--field']):
            params['fl[{}]'.format(i)] = f
        search(args['--search'],
               params=params,
               callback=callback,
               mine_ids=args['--mine-ids'],
               max_tasks=args['--workers'],
               retries=args['--retries'],
               secure=args['--secure'],
               hosts=args['--hosts'])
        sys.exit(0)
    else:
        # Exit with 2 if stdin appears to be empty.
        if args['-']:
            if (not os.fstat(sys.stdin.fileno()).st_size > 0) and (sys.stdin.seekable()):
                sys.exit(2)

        mine_items(args['<itemlist>'],
                   max_tasks=args['--workers'],
                   retries=args['--retries'],
                   secure=args['--secure'],
                   hosts=args['--hosts'])
