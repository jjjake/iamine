#!/usr/bin/env python3
"""Concurrently retrieve metadata from Archive.org items.

usage: ia-mine [-h] [--version] [--workers WORKERS] [--cache]
               [--retries RETRIES] [--secure] [--hosts HOSTS]
               [<itemlist> | -]

positional arguments:
  itemlist              A file containing Archive.org identifiers, one per
                        line, for which to retrieve metadata from. If no
                        itemlist is provided, identifiers will be read from
                        stdin.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
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
import os
import sys

from docopt import docopt, DocoptExit
from schema import Schema, Use, Or, SchemaError

from .api import mine_items
from ._version import __version__


def main(argv=None):
    # If ia-wrapper calls main with argv argument, strip the
    # "mine" subcommand from args. 
    argv = argv[1:] if argv else sys.argv[1:]

    # Catch DocoptExit error and write to stderr manually.
    # Otherwise error's vanish if executed from a pex binary. 
    try:
        args = docopt(__doc__, version=__version__, argv=argv, help=False)
    except DocoptExit as exc:
        sys.exit(sys.stderr.write('{}\n'.format(exc.code)))

    # Validate args.
    open_file_or_stdin = lambda f: sys.stdin if (f == '-') or (not f) else open(f)
    parse_hosts = lambda f: [x.strip() for x in open(f) if x.strip()]
    schema = Schema({
        '-': bool,
        '--cache': bool,
        '--help': bool,
        '--hosts': Or(None, 
            Use(parse_hosts, error='--hosts=HOSTS should be a readable file.')),
        '--retries': Use(int, 'RETRIES should be an integer.'),
        '--secure': bool,
        '--version': bool,
        '<itemlist>': Use(open_file_or_stdin, error='<itemlist> should be readable'),
        '--workers': Use(int, error='--workers=WORKERS should be an integer.'),
    })
    try:
        args = schema.validate(args)
    except SchemaError as exc:
        sys.exit(sys.stderr.write('{0}error: {1}\n'.format(__doc__, str(exc))))

    # Exit with 2 if stdin appears to be empty.
    if args['-']:
        if (not os.fstat(sys.stdin.fileno()).st_size > 0) and (sys.stdin.seekable()):
            sys.exit(2)

    # Launch miner.
    mine_items(args['<itemlist>'],
               max_tasks=args['--workers'],
               cache=args['--cache'],
               retries=args['--retries'],
               secure=args['--secure'],
               hosts=args['--hosts'])
