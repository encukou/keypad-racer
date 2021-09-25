import os
from pathlib import PurePosixPath
import atexit
try:
    import importlib_resources
except ImportError:
    from importlib import resources as importlib_resources

from . import __name__ as pkg_name

resource = importlib_resources.files(pkg_name)

def get_text(name):
    return resource.joinpath(name).read_text()

def open(name, *args, **kwargs):
    return resource.joinpath(name).open(*args, **kwargs)

def path(name, *args, **kwargs):
    return resource.joinpath(name).path()

def global_fspath(name):
    as_file = importlib_resources.as_file(resource.joinpath(name))
    path = as_file.__enter__()
    atexit.register(lambda: path.__exit__(None, None, None))
    return path

def get_shader(name):
    path = PurePosixPath(name)
    shader = ''.join(_shader_lines(path))
    #print(f'--{name}--')
    #print(shader)
    if 'VALIDATE_SHADERS' in os.environ:
        import subprocess
        subprocess.run(
            ['glslangValidator', '--stdin', '-S', path.suffix[1:]],
            input=shader,
            encoding='utf-8',
            check=True,
        )
    return shader

INCLUDE_DIRECTIVE = '#include '
VERSION_DIRECTIVE = '#version '
def _shader_lines(name, needed_version=None, included_from=None):
    version = None
    with resource.joinpath(name).open(encoding='utf-8') as f:
        for lineno, line in enumerate(f, start=1):
            if not line.endswith('\n'):
                raise ValueError(f'{name}:{lineno}: Unterminated line')
            if line.startswith(INCLUDE_DIRECTIVE):
                yield '#line 1\n'
                included_name = line[len(INCLUDE_DIRECTIVE):].strip()
                included_path = name.parent / included_name
                yield from _shader_lines(
                    included_path,
                    needed_version=version,
                    included_from=name,
                )
                yield f'#line {lineno+1}\n'
            elif line.startswith(VERSION_DIRECTIVE):
                if version is not None:
                    raise ValueError(
                        f'{name}:{lineno}: Duplicate #version directive'
                    )
                version = line[len(VERSION_DIRECTIVE):]
                if needed_version is None:
                    yield line
                elif version != needed_version:
                    raise ValueError(
                        f"{name}:{lineno}: #version {version!r} does not match {needed_version!r} from including file"
                    )
                else:
                    yield '\n'
            else:
                yield line
