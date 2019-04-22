import os
import yaml
import re
import logging
from typing import Union

from parser import C


log = logging.getLogger('brick')


def parse(file_path: str) -> dict:
    mega = _parse_file(file_path)

    return mega # load megafile


def _parse_file(file_path: str) -> dict:
    root = {}
    file_path = os.path.normpath(file_path)
    file_path = os.path.abspath(file_path)
    try:
        with open(file_path, 'r') as file:
            file_body = file.read()

            # replace yaml-illegal `@` references with `__$`
            file_body = re.sub(
                r"([\s]*[a-zA-Z0-9_\-\s]+[:]?\s)@([a-zA-Z0-9_:]+)",
                r"\1__$\2", file_body)
            root = yaml.load(file_body, yaml.SafeLoader)
            root['selfpath'] = os.path.normpath(file_path)
            _load_imports(root)
            _load_binaries(root)
            _normalise_sizes(root)

    except FileNotFoundError:
        log.error(f'model file {file_path} not found')

    return root


def _validate_object(obj: dict, schema: str) -> dict:
    """ will throw if validations fails """

    # @TODO schema based validations here
    return obj


def _load_imports(file_obj: dict):
    """ modifies given object, loads all imports, triggers recursive parsing """

    for i, import_item in enumerate(file_obj.get('imports', [])):
        _validate_object(import_item, C.SCHEMA.IMPORTS)

        file_obj['imports'][i]['module'] = _parse_file(
            os.path.join(os.path.dirname(file_obj['selfpath']),
                         file_obj['imports'][i]['source']))


def _load_binaries(file_obj: dict):
    """
    modifies given object, checks part binaries existence
    does not read or load in memory anything yet
    """

    if file_obj.get('part') and file_obj['part'].get('model'):
        bin_file = file_obj['part']['model'].get('file')
        bin_filepath = os.path.join(file_obj['selfpath'], bin_file)
        bin_filepath = os.path.normpath(bin_filepath)
        bin_filepath = os.path.abspath(bin_filepath)
        file_obj['part']['model']['file'] = bin_filepath

        if not os.path.exists(bin_filepath):
            log.error(f'binary file not found {bin_filepath}')

        # @TODO actually load DFX binaries


def _normalise_sizes(file_obj: dict):
    """ modifies given object, recalculates all sizes to default """

    def _find_positions(branch: Union[dict, list], source_unit: str):

        # @TODO this is ugly, make it pythonic
        if isinstance(branch, dict):
            for node in branch:
                if node == 'position':
                    _validate_object(branch[node], C.SCHEMA.POSITION)
                    __normalise(branch[node], source_unit)
                else:
                    _find_positions(branch[node], source_unit)
        if isinstance(branch, list):
            for i, node in enumerate(branch):
                _find_positions(branch[i], source_unit)

    def __normalise(position: dict, source_unit):
        if position.get('x'):
            if isinstance(position['x'], dict):
                position['x']['min'] = position['x']['min'] * C.UNITS[source_unit]
                position['x']['max'] = position['x']['max'] * C.UNITS[source_unit]
                position['x']['step'] = position['x']['step'] * C.UNITS[source_unit]
            else:
                position['x'] = position['x'] * C.UNITS[source_unit]

        if position.get('y'):
            if isinstance(position['y'], dict):
                position['y']['min'] = position['y']['min'] * C.UNITS[source_unit]
                position['y']['max'] = position['y']['max'] * C.UNITS[source_unit]
                position['y']['step'] = position['y']['step'] * C.UNITS[source_unit]
            else:
                position['y'] = position['y'] * C.UNITS[source_unit]

        if position.get('z'):
            if isinstance(position['z'], dict):
                position['z']['min'] = position['z']['min'] * C.UNITS[source_unit]
                position['z']['max'] = position['z']['max'] * C.UNITS[source_unit]
                position['z']['step'] = position['z']['step'] * C.UNITS[source_unit]
            else:
                position['z'] = position['z'] * C.UNITS[source_unit]

    if file_obj.get('settings') and file_obj['settings'].get('default_unit'):
        _find_positions(file_obj, file_obj['settings']['default_unit'])

        file_obj['settings'].pop('default_unit')
        if not file_obj['settings']:
            file_obj.pop('settings')
