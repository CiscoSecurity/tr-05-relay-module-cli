import mock
import pytest

from relay.constants import (
    CLIENT_ID_ENVVAR,
    CLIENT_PASSWORD_ENVVAR,
)


@pytest.fixture(scope='function')
def env():
    mock_env = {
        key: '<{key}>'.format(key=key)
        for key in (CLIENT_ID_ENVVAR, CLIENT_PASSWORD_ENVVAR, 'NAME', 'URL')
    }

    with mock.patch('os.environ', mock_env):
        yield mock_env
