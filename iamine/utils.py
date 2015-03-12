import sys
import signal


def suppress_interrupt_messages():
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


def suppress_brokenpipe_messages():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
