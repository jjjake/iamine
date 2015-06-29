import sys
import signal

from .exceptions import AuthenticationError


def suppress_interrupt_messages():
    """Register a new excepthook to suppress KeyboardInterrupt
    exception messages, and exit with status code 130.

    """
    old_excepthook = sys.excepthook

    def new_hook(type, value, traceback):
        if type == KeyboardInterrupt:
            sys.exit(130)
        else:
            old_excepthook(type, value, traceback)

    sys.excepthook = new_hook


def suppress_brokenpipe_messages():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def handle_cli_exceptions():
    old_excepthook = sys.excepthook

    def new_hook(type, value, traceback):
        if type == AuthenticationError:
            if str(value).startswith('The request signature we calculated'):
                print('error: Your secret key does not match your access key.',
                       'Please rerun `ia-mine --configure`.', file=sys.stderr)
            elif str(value).startswith('The AWS Access Key Id'):
                print('error: Your access key is invalid.',
                       'Please rerun `ia-mine --configure`.', file=sys.stderr)
            sys.exit(1)
        else:
            old_excepthook(type, value, traceback)

    sys.excepthook = new_hook
