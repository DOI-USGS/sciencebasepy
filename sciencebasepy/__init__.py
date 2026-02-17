from .SbSession import SbSession

__author__ = 'sciencebase'

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sciencebasepy")
except PackageNotFoundError:
    __version__ = "Unknown or uninstalled"


