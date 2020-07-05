# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

from kusanagi.sdk import __license__
from kusanagi.sdk import __version__

setup(
    name='kusanagi-sdk-python',
    version=__version__,
    url='http://kusanagi.io/',
    license=__license__,
    author='Jerónimo Albi',
    author_email='jeronimo.albi@kusanagi.io',
    description='Python SDK for the KUSANAGI™ framework',
    platforms=['POSIX'],
    download_url='https://github.com/kusanagi/kusanagi-sdk-python/releases',
    namespace_packages=['kusanagi'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'pyzmq==19.0.0',
        'msgpack==1.0.0',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'pytest-mock',
        'pytest-mypy',
        'pylint',
        'pylama',
        'coverage',
        'isort',
        'flake8',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
)
