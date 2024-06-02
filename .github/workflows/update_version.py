#!/bin/python3
from json import load
from pathlib import Path

THIS_PATH = Path(__file__).resolve().parent.resolve()

# Paths
CHANGELOG_PATH = Path(f'{THIS_PATH}/../../debian/changelog')
CONTROL_PATH = Path(f'{THIS_PATH}/../../debian/control')
PKGBUILD_PATH = Path(f'{THIS_PATH}/../../PKGBUILD')
SETUPPY_PATH = Path(f'{THIS_PATH}/../../setup.py')
SETUPCFG_PATH = Path(f'{THIS_PATH}/../../setup.cfg')

VERSION = ''

with open(Path(f'{THIS_PATH}/../../package.json'), 'r') as package:
    data = load(package)
    VERSION = data['version']

def update_file(file_path, and_dashed=False):
    layout_path = Path(f'{THIS_PATH}/layout/{file_path.name}')

    with open(layout_path, 'r') as layout:
        data = layout.read()
        data = data.replace('$version', VERSION)

        if and_dashed:
            splitted_version = VERSION.split('.')
            DASHED_VERSION = f'{splitted_version[0]}.{splitted_version[1]}-{splitted_version[2]}'
            data = data.replace('$dashed_version', DASHED_VERSION)

        with open(file_path, 'w') as file:
            file.write(data)

if __name__ == '__main__':
    update_file(CHANGELOG_PATH)
    update_file(CONTROL_PATH, True)
    update_file(PKGBUILD_PATH)
    update_file(SETUPPY_PATH)
    update_file(SETUPCFG_PATH)