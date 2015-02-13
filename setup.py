from setuptools import setup
import sys


if sys.version_info <= (3,):
    sys.stderr.write('"iamine" requires a Python version greater than 3.3.')
    sys.exit(1)

install_requires = [
    'aiohttp==0.13.1',
]

if sys.version_info <= (3,4):
    install_requires.append('asyncio==3.4.1')

setup(
    name = 'iamine',
    version = '0.5',
    author='Jacob M. Johnson',
    author_email='jake@archive.org',
    url='https://github.com/jjjake/iamine',
    license='AGPL 3',
    description='Concurrently retrieve metadata from Archive.org items.',
    packages=['iamine'],
    install_requires = install_requires,
    entry_points = {
        'console_scripts': [
            'ia-mine = iamine:main',
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
