from setuptools import setup


setup(
    name = 'iamine',
    version = '0.1',
    packages=['iamine'],
    install_requires = [
        'aiohttp==0.14.1',
        'asyncio==3.4.1'
    ],
    entry_points = {
        'console_scripts': [
            'ia-mine = iamine:main',
        ],
    }
)
