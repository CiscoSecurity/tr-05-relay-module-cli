import json
import os
import string

import cerberus
import six

from relay.constants import (
    RELAY_MODULE_SUPPORTED_APIS,
)
from relay.exceptions import SettingsValidationError


settings_schema = {
    'name': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'module_type_id': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'visibility': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'settings': {
        'type': 'dict',
        'required': True,
        'empty': False,
        'schema': {
            'url': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'supported-apis': {
                'type': 'list',
                'required': True,
                'empty': False,
                'allowed': RELAY_MODULE_SUPPORTED_APIS,
            },
        },
        'allow_unknown': True,
    },
}
settings_validator = cerberus.Validator(settings_schema)


def _expand(text):
    """
    Expand a text with the environment variables.
    The text itself is assumed (but not required) to be a template containing
    some placeholders and having the following format:
    1. "...$COLOR...";
    2. "...${COLOR}...";
    3. "...${COLOR}ish...".
    If an environment variable named `COLOR` is defined, the corresponding
    placeholders in the template will be replaced with the actual value of it.
    Otherwise, an instance of `KeyError` will be raised.
    """
    return string.Template(text).substitute(os.environ)


def load_settings(settings_file):
    """
    Load (parse & validate) the Relay settings JSON from a file object.
    """

    try:
        settings = json.load(settings_file)
    except ValueError:
        message = (
            'Unable to load Relay settings JSON file. '
            'It may be malformed.'
        )
        raise SettingsValidationError(message)

    try:
        if not settings_validator.validate(settings):
            message = (
                'Invalid Relay settings JSON schema:\n' +
                json.dumps(settings_validator.errors, indent=2)
            )
            raise SettingsValidationError(message)

    except Exception:
        message = (
            'Invalid Relay settings JSON schema. '
            'It must conform to:\n' +
            json.dumps(settings_schema, indent=2) + '\n'
            'Check '
            'https://docs.python-cerberus.org/en/stable/validation-rules.html '
            'for more insight on validation rules.'
        )
        raise SettingsValidationError(message)

    try:
        settings['name'] = _expand(settings['name'])

        for key, value in settings['settings'].items():
            # Do not go too deep, keep it simple.
            if isinstance(value, six.text_type):
                settings['settings'][key] = _expand(value)

    except KeyError as error:
        key = error.args[0]
        message = (
            'Unable to read environment variable "{}" '
            'for Relay settings JSON expansion. '
            'Make sure to define it first.'
        ).format(key)
        raise SettingsValidationError(message)

    return settings
