import re
import ast
import sys
from setuptools import setup
from codecs import open


_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('iamine/__init__.py', 'rb', 'utf-8') as f:
    version = str(ast.literal_eval(_version_re.search(f.read()).group(1)))

if sys.version_info <= (3,):
    sys.stderr.write('"iamine" requires a Python version greater than 3.3.')
    sys.exit(1)

install_requires = [
    'aiohttp==0.13.1',
    'schema==0.3.1',
    'docopt==0.6.1',
]

if sys.version_info <= (3,4):
    install_requires.append('asyncio==3.4.1')

setup(
    name = 'iamine',
    version = version,
    author='Jacob M. Johnson',
    author_email='jake@archive.org',
    url='https://github.com/jjjake/iamine',
    license='AGPL 3',
    description='Concurrently retrieve metadata from Archive.org items.',
    packages=['iamine'],
    install_requires = install_requires,
    entry_points = {
        'internetarchive.plugins': [
            'Miner = iamine.core:Miner',
            'mine_items = iamine.api:mine_items',
        ],
        'internetarchive.cli.plugins': [
            'ia_mine = iamine.__main__',
        ],
        'console_scripts': [
            'ia-mine = iamine.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
)
