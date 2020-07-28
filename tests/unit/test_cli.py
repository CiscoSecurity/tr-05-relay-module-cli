import json
import uuid

import mock
import pytest
from click.testing import CliRunner

from relay.cli import relay
from relay.constants import (
    RELAY_MODULE_SUPPORTED_APIS,
    SETTINGS_FILE_DEFAULT,
    CLIENT_ID_ENVVAR,
    CLIENT_PASSWORD_ENVVAR,
)


def settings_data():
    return {
        'name': '${NAME}',
        'module_type_id': 'a14ae422-01b6-5013-9876-695ff1b0ebe0',
        'visibility': 'org',
        'settings': {
            'url': '$URL',
            'supported-apis': list(RELAY_MODULE_SUPPORTED_APIS),
        },
    }


@pytest.fixture(scope='function')
def runner():
    runner = CliRunner()

    with runner.isolated_filesystem():
        with open(SETTINGS_FILE_DEFAULT, 'w') as settings_file:
            settings_file.write(json.dumps(settings_data()))

        yield runner


@pytest.fixture(scope='function')
def tr():
    with mock.patch('relay.cli.ThreatResponse') as mock_tr:
        mock_tr.instance = mock_tr.return_value = mock.MagicMock()
        yield mock_tr


@pytest.fixture(scope='module', params=('add', 'edit', 'remove'))
def command(request):
    return request.param


def test_invoke_relay_command_tr_connection_error(env, runner, tr, command):
    message = 'Unable to connect to Threat Response.'

    tr.side_effect = RuntimeError(message)

    result = runner.invoke(relay, [command])

    assert result.exit_code == 1
    assert result.output == 'Error: {message}\n'.format(message=message)

    tr.assert_called_once_with(env[CLIENT_ID_ENVVAR],
                               env[CLIENT_PASSWORD_ENVVAR])


def test_invoke_relay_command_settings_loading_error(env, runner, tr, command):
    del env['NAME']

    message = ('Unable to read environment variable "NAME" for Relay settings '
               'JSON expansion. Make sure to define it first.')

    result = runner.invoke(relay, [command])

    assert result.exit_code == 1
    assert result.output == 'Error: {message}\n'.format(message=message)

    tr.assert_called_once_with(env[CLIENT_ID_ENVVAR],
                               env[CLIENT_PASSWORD_ENVVAR])


def test_invoke_relay_command_processing_error(env, runner, tr, command):
    if command == 'add':
        modules = [{
            'name': env['NAME'],
            'module_type_id': 'a14ae422-01b6-5013-9876-695ff1b0ebe0',
            'visibility': 'org',
            'settings': {
                'url': env['URL'],
                'supported-apis': list(RELAY_MODULE_SUPPORTED_APIS),
            },
            'id': str(uuid.uuid4()),
        }]

        message = ('Relay module "{name}" already '
                   'exists!'.format(name=env['NAME']))

    elif command in ('edit', 'remove'):
        modules = []

        message = ('Relay module "{name}" does not '
                   'exist!'.format(name=env['NAME']))

    else:
        assert False, 'Unknown command: {command}.'.format(command=command)

    tr.instance.int.module_instance.get.return_value = modules

    result = runner.invoke(relay, [command])

    assert result.exit_code == 1
    assert result.output == 'Error: {message}\n'.format(message=message)

    tr.assert_called_once_with(env[CLIENT_ID_ENVVAR],
                               env[CLIENT_PASSWORD_ENVVAR])

    tr.instance.int.module_instance.get.assert_called_once_with()


def test_invoke_relay_command_ok(env, runner, tr, command):
    message = ('Relay module "{name}" has been successfully '
               '{{commanded}}!'.format(name=env['NAME']))

    if command == 'add':
        modules = []

        message = message.format(commanded='added')

    elif command in ('edit', 'remove'):
        modules = [{
            'name': env['NAME'],
            'module_type_id': 'a14ae422-01b6-5013-9876-695ff1b0ebe0',
            'visibility': 'org',
            'settings': {'foo': 'bar'},
            'id': str(uuid.uuid4()),
        }]

        commanded = {'edit': 'edited', 'remove': 'removed'}[command]
        message = message.format(commanded=commanded)

    else:
        assert False, 'Unknown command: {command}.'.format(command=command)

    tr.instance.int.module_instance.get.return_value = modules

    result = runner.invoke(relay, [command])

    assert result.exit_code == 0
    assert result.output == '{message}\n'.format(message=message)

    tr.assert_called_once_with(env[CLIENT_ID_ENVVAR],
                               env[CLIENT_PASSWORD_ENVVAR])

    tr.instance.int.module_instance.get.assert_called_once_with()

    settings = settings_data()

    settings['name'] = env['NAME']
    settings['settings']['url'] = env['URL']

    if command == 'add':
        module = settings

        args = (module,)
        tr.instance.int.module_instance.post.assert_called_once_with(*args)

    elif command == 'edit':
        module_id = modules[0]['id']
        diff = {'settings': settings['settings']}

        args = (module_id, diff)
        tr.instance.int.module_instance.patch.assert_called_once_with(*args)

    elif command == 'remove':
        module_id = modules[0]['id']

        args = (module_id,)
        tr.instance.int.module_instance.delete.assert_called_once_with(*args)

    else:
        assert False, 'Unknown command: {command}.'.format(command=command)
