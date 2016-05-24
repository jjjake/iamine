"""
IA Mine
~~~~~~~

Internet Archive data mining tools.

:copyright: (c) 2015 by Internet Archive.
:license: AGPL 3, see LICENSE for more details.

"""
__title__ = 'iamine'
__version__ = '0.3.6'
__url__ = 'https://github.com/jjjake/iamine'
__author__ = 'Jacob M. Johnson'
__license__ = 'AGPL 3'
__copyright__ = 'Copyright 2015 Internet Archive'


from .api import mine_items, search, mine_urls, configure


__all__ = ['mine_items', 'search', 'mine_urls', '__version__', 'configure']
