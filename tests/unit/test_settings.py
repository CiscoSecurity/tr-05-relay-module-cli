import json
import tempfile

import pytest

from relay.constants import (
    RELAY_MODULE_SUPPORTED_APIS,
)
from relay.exceptions import SettingsValidationError
from relay.settings import load_settings


@pytest.fixture(scope='function')
def settings_file():
    with tempfile.NamedTemporaryFile('w+') as mock_settings_file:
        yield mock_settings_file


def write_to(file, text):
    file.seek(0)
    file.truncate(0)

    file.write(text)
    file.flush()

    file.seek(0)


def test_load_settings_json_decoding_error(settings_file):
    write_to(settings_file, 'Hello, World!')

    with pytest.raises(SettingsValidationError):
        load_settings(settings_file)


def test_load_settings_schema_validation_error(settings_file):
    write_to(settings_file, json.dumps(['Hello, World!']))

    with pytest.raises(SettingsValidationError):
        load_settings(settings_file)

    write_to(settings_file, json.dumps({'message': 'Hello, World!'}))

    with pytest.raises(SettingsValidationError):
        load_settings(settings_file)


def settings_data():
    return {
        'name': '$NAME',
        'module_type_id': 'a14ae422-01b6-5013-9876-695ff1b0ebe0',
        'visibility': 'org',
        'settings': {
            'url': '$URL',
            'supported-apis': list(RELAY_MODULE_SUPPORTED_APIS),
        },
    }


def test_load_settings_ok(env, settings_file):
    data = settings_data()

    write_to(settings_file, json.dumps(data))

    settings = load_settings(settings_file)

    data['name'] = env['NAME']
    data['settings']['url'] = env['URL']

    assert settings == data


def test_load_settings_expansion_error(env, settings_file):
    del env['NAME']

    data = settings_data()

    write_to(settings_file, json.dumps(data))

    with pytest.raises(SettingsValidationError):
        load_settings(settings_file)
