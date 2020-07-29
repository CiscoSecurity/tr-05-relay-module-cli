import os

import pytest
from click.testing import CliRunner
from threatresponse import ThreatResponse

from relay.cli import relay


CTR_CLIENT_ID = os.environ['CLIENT_ID_ENVVAR']
CTR_CLIENT_PASSWORD = os.environ['CLIENT_PASSWORD_ENVVAR']

MODULE_NAME = 'Test Automation Mock'

os.environ['NAME'] = MODULE_NAME
os.environ['OLD_URL'] = 'https://old.execute-api.region.amazonaws.com/qa'
os.environ['NEW_URL'] = 'https://new.execute-api.region.amazonaws.com/qa'
os.environ['JWT'] = 'Cisco.Threat.Response'

SETTINGS_FILE_PATH = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__),
        '../data/relay_settings.json'
    )
)
EDITED_SETTINGS_FILE_PATH = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__),
        '../data/edited_relay_settings.json'
    )
)

runner = CliRunner()


def get_module(module_name=MODULE_NAME):
    tr = ThreatResponse(CTR_CLIENT_ID, CTR_CLIENT_PASSWORD)

    modules = tr.int.module_instance.get()

    return next(
        (module for module in modules if module['name'] == module_name),
        None
    )


@pytest.fixture(scope='function')
def reset_test_module():
    def cleanup():
        if get_module():
            runner.invoke(relay, [
                'remove',
                '-i', CTR_CLIENT_ID,
                '-p', CTR_CLIENT_PASSWORD,
                '-f', SETTINGS_FILE_PATH
            ])

    cleanup()
    yield cleanup
    cleanup()


def test_positive_add_module(reset_test_module):
    """Perform testing of adding new test module through CLI lambda relay
    interface

    ID: CCTRI-396-a9a9d99a-a57f-4b41-887b-7b5c1742b489

    Pre-conditions: Test module is removed from CTR application

    Steps:

        1. Call 'add' command from CLI module with default parameters

    Expectedresults: New test module is added to CTR application

    Importance: High
    """
    result = runner.invoke(relay, [
        'add',
        '-i', CTR_CLIENT_ID,
        '-p', CTR_CLIENT_PASSWORD,
        '-f', SETTINGS_FILE_PATH
    ])
    assert result.exit_code == 0
    assert (
        f'Relay module "{MODULE_NAME}" has been successfully added!'
        in result.output
    )
    assert get_module()['name'] == MODULE_NAME


def test_positive_edit_module(reset_test_module):
    """Perform testing of editing existing test module through CLI lambda relay
    interface

    ID: CCTRI-396-8bae66b5-4744-4d17-bd5d-1057cbd1c1e1

    Pre-conditions: Test module is removed from CTR application

    Steps:

        1. Call 'add' command from CLI module with default parameters
        2. Call 'edit' command for just created module

    Expectedresults: Test module is successfully modified with other values

    Importance: Medium
    """
    result = runner.invoke(relay, [
        'add',
        '-i', CTR_CLIENT_ID,
        '-p', CTR_CLIENT_PASSWORD,
        '-f', SETTINGS_FILE_PATH
    ])
    assert result.exit_code == 0
    assert get_module()['settings']['url'] == os.environ['OLD_URL']
    result = runner.invoke(relay, [
        'edit',
        '-i', CTR_CLIENT_ID,
        '-p', CTR_CLIENT_PASSWORD,
        '-f', EDITED_SETTINGS_FILE_PATH
    ])
    assert result.exit_code == 0
    assert (
        f'Relay module "{MODULE_NAME}" has been successfully edited!'
        in result.output
    )
    assert get_module()['settings']['url'] == os.environ['NEW_URL']


def test_positive_remove_module(reset_test_module):
    """Perform testing of removing existing test module through CLI lambda
    relay interface

    ID: CCTRI-396-2791918d-6562-4087-8070-e00b7655ce53

    Pre-conditions: Test module is removed from CTR application

    Steps:

        1. Call 'add' command from CLI module with default parameters
        2. Call 'remove' command for just created module

    Expectedresults: Test module is successfully removed from CTR application
        with corresponding message

    Importance: High
    """
    result = runner.invoke(relay, [
        'add',
        '-i', CTR_CLIENT_ID,
        '-p', CTR_CLIENT_PASSWORD,
        '-f', SETTINGS_FILE_PATH
    ])
    assert result.exit_code == 0
    result = runner.invoke(relay, [
        'remove',
        '-i', CTR_CLIENT_ID,
        '-p', CTR_CLIENT_PASSWORD,
        '-f', EDITED_SETTINGS_FILE_PATH
    ])
    assert result.exit_code == 0
    assert (
        f'Relay module "{MODULE_NAME}" has been successfully removed!'
        in result.output
    )
    assert get_module() is None


def test_negative_add_module(reset_test_module):
    """Perform testing of adding test module to the system with a name of
    existing one

    ID: CCTRI-396-e7fc31ca-0454-476f-8b90-f904f0a0cb4b

    Pre-conditions: Test module is removed from CTR application

    Steps:

        1. Call 'add' command from CLI module with default parameters
        2. Call 'add' command once more with the same parameters

    Expectedresults: Error message is displayed

    Importance: Medium
    """
    result = runner.invoke(relay, [
        'add',
        '-i', CTR_CLIENT_ID,
        '-p', CTR_CLIENT_PASSWORD,
        '-f', SETTINGS_FILE_PATH
    ])
    assert result.exit_code == 0
    result = runner.invoke(relay, [
        'add',
        '-i', CTR_CLIENT_ID,
        '-p', CTR_CLIENT_PASSWORD,
        '-f', SETTINGS_FILE_PATH
    ])
    assert result.exit_code == 1
    assert (
        f'Error: Relay module "{MODULE_NAME}" already exists!'
        in result.output
    )
