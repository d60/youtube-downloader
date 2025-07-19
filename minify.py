import platform
import subprocess
from pathlib import Path


def _get_subprocess_command(command):
    if platform.system() == 'Windows':
        return ['cmd', '/c'] + command
    else:
        return command


def _minify_js(dir: Path, outdir: Path):
    for file in dir.iterdir():
        if '.min.' in file.name:
            continue
        output = outdir / f'{file.stem}.min{file.suffix}'
        command = [
            'uglifyjs',
            f'{file.as_posix()}',
            '-o', f'{output.as_posix()}',
            '--mangle', 'toplevel,eval',
            '--compress', 'pure_getters,passes=3,unsafe,unsafe_comps,collapse_vars,reduce_vars,toplevel,merge_vars,sequences',
            '--toplevel',
            '--rename'
        ]
        subprocess.run(_get_subprocess_command(command))


def _minify_css(dir: Path, outdir: Path):
    for file in dir.iterdir():
        if '.min.' in file.name:
            continue
        output = outdir / f'{file.stem}.min{file.suffix}'
        command = [
            'cleancss',
            f'{file.as_posix()}',
            '-o', f'{output.as_posix()}'
        ]
        subprocess.run(_get_subprocess_command(command))


def minify():
    _minify_js(Path('./static_/js'), Path('./static/js'))
    _minify_css(Path('./static_/css/'), Path('./static/css/'))

if __name__ == '__main__':
    minify()
