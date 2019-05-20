import os
import yaml
import re
import logging
from typing import Union

from parser import C


log = logging.getLogger('brick')
log.setLevel(logging.DEBUG)

_file_index = dict()
_named_objects = dict()


def parse(file_path: str) -> dict:
    """
    Will recursively parse all imports and populate the file index.
    Returns index.
    """
    global _file_index, _named_objects

    # this should parse the whole tree and populate the _file_index
    _parse_file(file_path)

    for index_file_path in _file_index:
        _parse_named_objects(index_file_path)
        _resolve_imports(index_file_path)

    return _file_index


def _parse_file(file_path: str) -> None:
    """
    Parses the given filepath and addes it to global _file_index.
    Triggers parsing of imports and recursive parsing of files. """
    global _file_index

    file_path = os.path.normpath(file_path)
    file_path = os.path.abspath(file_path)
    try:
        with open(file_path, 'r') as file:
            file_body = file.read()

            # replace yaml-illegal `@` references with `brick://` URI schema
            file_body = re.sub(
                r"([\s]*[a-zA-Z0-9_\-\s]+[:]?\s)@([a-zA-Z0-9_:]+)",
                r"\1brick://\2", file_body)
            file_obj = yaml.load(file_body, yaml.SafeLoader)
            _file_index[file_path] = file_obj
            _parse_imports(file_obj, file_path)
            _load_binaries(file_obj, file_path)
            _normalise_sizes(file_obj)

    except FileNotFoundError:
        log.error(f'model file {file_path} not found')


def _parse_imports(file_obj: dict, file_path: str):
    """ loads all imports, triggers recursive parsing """

    for i, import_item in enumerate(file_obj.get('imports', [])):
        import_path = os.path.join(os.path.dirname(file_path),
                                   file_obj['imports'][i]['source'])
        _parse_file(import_path)


def _parse_named_objects(file_path: str):
    """
    traverses the file_obj tree and indexes all named objects
    with it's full paths
    """
    global _file_index, _named_objects
    if not _named_objects.get(file_path):
        _named_objects[file_path] = dict()

    def __find_named_objects(branch: dict, branch_path: str):
        # `branch` may be dict or list
        branch_nodes = branch.keys() if isinstance(branch, dict) \
                                     else range(len(branch))
        for node in branch_nodes:
            if isinstance(branch[node], dict) and branch[node].get('name'):
                named_obj_ref = None
                if branch_path.endswith('imports:'):
                    import_path = os.path.join(os.path.dirname(file_path),
                                               branch[node].get('source'))
                    import_path = os.path.abspath(import_path)
                    import_path = os.path.normpath(import_path)

                    # if top level has `block` node - reference it by default
                    if _file_index[import_path].get('block'):
                        named_obj_ref = f"{import_path}:block"

                    # elif top level has `part` node - reference it instead
                    elif _file_index[import_path].get('part'):
                        named_obj_ref = f"{import_path}:part"
                    else:
                        log.error(f"import top node not found, "
                                  f"path: `{import_path}` "
                                  f"file: `{file_path}`")
                else:
                    named_obj_ref = f"{branch_path}{node}"

                _named_objects[file_path][branch[node]['name']] = named_obj_ref
            elif type(branch[node]) in (dict, list):
                __find_named_objects(branch[node], f"{branch_path}{node}:")

    __find_named_objects(_file_index[file_path], f"{file_path}:")


def _resolve_imports(file_path: str):
    """
    modifies given object, recursively checks all contents of an object and
    resolves all `brick://` relative import URIs into absolute URIs according
    to _file_index.
    """
    global _file_index

    def __find_import_path(import_reference: str) -> str:
        imports_list = _file_index[file_path].get('imports', [])
        for import_obj in imports_list:
            if import_obj.get('name') == import_reference:
                import_path = os.path.join(os.path.dirname(file_path),
                                           import_obj.get('source'))
                return import_path

    def __find_replace_imports(branch: dict, branch_path: str):
        # `branch` may be dict or list
        branch_nodes = branch.keys() if isinstance(branch, dict) \
                                     else range(len(branch))
        for node in branch_nodes:
            if isinstance(branch[node], str):
                if branch[node].startswith('brick://') \
                        and ":" not in branch[node][8:]:
                    import_path = __find_import_path(branch[node][8:])

                    if _file_index.get(import_path):
                        branch[node] = f"brick://{import_path}"
                    else:
                        log.error(
                            f"import not found, "
                            f"reference: `{branch[node][8:]}` "
                            # f"path: `{import_path}` "
                            f"file: `{file_path}` ")
            elif type(branch[node]) in (dict, list):
                __find_replace_imports(branch[node], f"{branch_path}{node}:")

    __find_replace_imports(_file_index[file_path], f"{file_path}:")


def _load_binaries(file_obj: dict, file_path: str):
    """
    modifies given object, checks part binaries existence
    does not read or load anything into memory yet
    """

    if file_obj.get('part') and file_obj['part'].get('model'):
        bin_file = file_obj['part']['model'].get('file')
        bin_filepath = os.path.join(os.path.dirname(file_path),
                                    bin_file)
        bin_filepath = os.path.normpath(bin_filepath)
        bin_filepath = os.path.abspath(bin_filepath)
        file_obj['part']['model']['file'] = bin_filepath

        if not os.path.exists(bin_filepath):
            log.error(f'binary file not found {bin_filepath}')


def _normalise_sizes(file_obj: dict):
    """ modifies given object, recalculates all sizes to default """

    def _find_positions(branch: Union[dict, list], source_unit: str):

        # @TODO this is ugly, make it pythonic
        if isinstance(branch, dict):
            for node in branch:
                if node == 'position':
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
