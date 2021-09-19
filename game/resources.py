from pathlib import PurePosixPath
try:
    import importlib_resources
except ImportError:
    from importlib import resources as importlib_resources

from . import __name__ as pkg_name

resource = importlib_resources.files(pkg_name)

def get_text(name):
    return resource.joinpath(name).read_text()

def get_shader(name):
    shader = ''.join(_shader_lines(PurePosixPath(name)))
    print(f'--{name}--')
    print(shader)
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
