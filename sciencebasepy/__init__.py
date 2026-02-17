from .SbSession import SbSession
# from pkg_resources import get_distribution
# from pkg_resources import DistributionNotFound

__author__ = 'sciencebase'

# try:
#     __version__ = get_distribution("sciencebasepy").version
# except DistributionNotFound:
#     __version__ = 'NOT_INSTALLED'


from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sciencebasepy")
except PackageNotFoundError:
    __version__ = "Unknown or uninstalled"


