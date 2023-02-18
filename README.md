Python SDK for the KUSANAGI framework
=====================================

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Tests](https://github.com/kusanagi/kusanagi-sdk-python/actions/workflows/test.yml/badge.svg)

**Python** SDK to interface with the **KUSANAGI**™ framework (http://kusanagi.io).

Requirements
------------

* [KUSANAGI framework](http://kusanagi.io) 5.0+
* [Python](https://www.python.org/downloads/) 3.9+
* [libzmq](http://zeromq.org/intro:get-the-software) 4.3.4+

Installation
------------

Enter the following command to install the SDK in your local environment:

```
$ pip install kusanagi-sdk-python
```

[Poetry](https://python-poetry.org/docs/#installation) is required to run the test, coverage and linting.

The tests run using `pytest`:

```
$ poetry run pytest
```

Or to run the tests with coverage:

```
$ poetry run pytest --cov=kusanagi
```

Alternativelly the tests and coverage can be run for the supported python versions though
[tox](https://tox.wiki/en/latest/) by running:

```
$ tox
```

Getting Started
---------------

See the [getting started](http://kusanagi.io/docs/getting-started) tutorial to begin with the **KUSANAGI**™ framework and the **Python** SDK.

Documentation
-------------

See the [API](http://kusanagi.io/docs/sdk) for a technical reference of the SDK.

For help using the framework see the [documentation](http://kusanagi.io/docs).

Support
-------

Please first read our [contribution guidelines](http://kusanagi.io/open-source/contributing).

* [Requesting help](http://kusanagi.io/open-source/help)
* [Reporting a bug](http://kusanagi.io/open-source/bug)
* [Submitting a patch](http://kusanagi.io/open-source/patch)
* [Security issues](http://kusanagi.io/open-source/security)

We use [milestones](https://github.com/kusanagi/kusanagi-sdk-python/milestones) to track upcoming releases inline with our [versioning](http://kusanagi.io/open-source/roadmap#versioning) strategy, and as defined in our [roadmap](http://kusanagi.io/open-source/roadmap).

Contributing
------------

If you'd like to know how you can help and support our Open Source efforts see the many ways to [get involved](http://kusanagi.io/open-source).

Please also be sure to review our [community guidelines](http://kusanagi.io/open-source/conduct).

License
-------

Copyright 2016-2023 KUSANAGI S.L. (http://kusanagi.io). All rights reserved.

KUSANAGI, the sword logo and the "K" logo are trademarks and/or registered trademarks of KUSANAGI S.L. All other trademarks are property of their respective owners.

Licensed under the [MIT License](https://opensource.org/licenses/MIT). Redistributions of the source code included in this repository must retain the copyright notice found in each file.
