# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


class Singleton(type):
    """
    Metaclass to make a class definition a singleton.

    The class definition using this will contain a class property
    called `instance` with the only instance allowed for that class.

    Instance is, of course, only created the first time the class is called.

    """

    def __init__(cls, name: str, bases: tuple, classdict: dict):
        super().__init__(name, bases, classdict)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)

        return cls.instance
