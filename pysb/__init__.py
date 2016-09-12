from .SbSession import SbSession
from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound

__author__ = 'sciencebase'

try:
    __version__ = get_distribution("pysb").version
except DistributionNotFound:
    __version__ = 'NOT_INSTALLED'

