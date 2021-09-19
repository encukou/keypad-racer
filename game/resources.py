try:
    import importlib_resources
except ImportError:
    from importlib import resources as importlib_resources

from . import __name__ as pkg_name

resource = importlib_resources.files(pkg_name)

def get_text(name):
    return resource.joinpath(name).read_text()
