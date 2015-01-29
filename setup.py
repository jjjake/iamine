from setuptools import setup


setup(
    name = 'iamine',
    version = '0.2',
    author='Jacob M. Johnson',
    author_email='jake@archive.org',
    url='https://github.com/jjjake/iamine',
    license='AGPL 3',
    description='Concurrently retrieve metadata from Archive.org items.',
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
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
)
