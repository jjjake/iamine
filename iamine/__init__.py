#!/usr/bin/env python3
"""
IA Mine
~~~~~~~

Concurrently retrieve metadata from Archive.org items.

:copyright: (c) 2015 by Internet Archive.
:license: AGPL 3, see LICENSE for more details.
"""
__title__ = 'iamine'
__version__ = '0.2.1'
__author__ = 'Jacob M. Johnson'
__license__ = 'AGPL 3'
__copyright__ = 'Copyright 2015 Internet Archive'


from .core import Miner
from .api import get_miner, mine_items, search, mine_urls


__all__ = ['Miner', 'get_miner', 'mine_items', 'search', '__version__', 'mine_urls']
