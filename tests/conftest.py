import pytest


@pytest.fixture(scope='session')
def headers():
    """ default HTTP headers for all API calls """
    return {"Content-type": "application/json"}


def pytest_addoption(parser):
    parser.addoption("--list", action="store_true",
                     default=False, help="Print all test items "
                                         "in path reference format.")


def pytest_collection_finish(session):
    if session.config.option.list:
        for item in session.items:
            print(f'{item.nodeid}')

        pytest.exit(f'{len(session.items)} tests')
