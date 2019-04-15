from typing import NamedTuple


class SchemaTuple(NamedTuple):
    IMPORTS: dict
    POSITION: dict


class DefaultsTuple(NamedTuple):
    UNIT: str # hardcoded to meters for now


SCHEMA = SchemaTuple(dict(), dict())
DEFAULTS = DefaultsTuple('m')

UNITS = {
    'km': 1000,
    'm': 1,
    'cm': 0.01,
    'mm': 0.001,
}
