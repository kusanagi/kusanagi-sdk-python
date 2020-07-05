# See https://setuptools.readthedocs.io/en/latest/setuptools.html#namespace-packages
# pragma: no cover
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:  # pragma: no cover
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
