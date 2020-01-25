# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

from kusanagi import __license__
from kusanagi import __version__

setup(
    name='kusanagi-sdk-python',
    version=__version__,
    url='http://kusanagi.io/',
    license=__license__,
    author='Jerónimo Albi',
    author_email='jeronimo.albi@kusanagi.io',
    description='Python SDK for the KUSANAGI framework',
    platforms=['POSIX'],
    download_url='https://github.com/kusanagi/kusanagi-sdk-python/releases',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'click==7.0',
        'pyzmq==17.1.2',
        'msgpack-python==0.5.6',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-mock',
        'pytest-cov',
        'pylint',
        'pylama',
        'coverage',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
)
