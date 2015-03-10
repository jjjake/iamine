#!/usr/bin/env python3
"""
IA Mine
~~~~~~~

Concurrently retrieve metadata from Archive.org items.

:copyright: (c) 2015 by Internet Archive.
:license: AGPL 3, see LICENSE for more details.

"""
__title__ = 'iamine'
__author__ = 'Jacob M. Johnson'
__license__ = 'AGPL 3'
__copyright__ = 'Copyright 2015 Internet Archive'

from ._version import __version__
from .core import Miner
from .api import mine_items, search

__all__ = ['Miner', 'mine_items', 'search', '__version__']
