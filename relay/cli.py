import click
from threatresponse import ThreatResponse

from relay.constants import (
    CLIENT_ID_ENVVAR,
    CLIENT_PASSWORD_ENVVAR,
    SETTINGS_FILE_DEFAULT,
)
from relay.exceptions import (
    ModuleAlreadyExistsError,
    ModuleDoesNotExistError,
    ModuleHasNotBeenChangedError,
)
from relay.settings import load_settings


@click.group()
def relay():
    pass


def relay_command(function):
    @click.command(function.__name__)
    @click.option(
        '-i', '--client_id',
        prompt='Client ID',
        envvar=CLIENT_ID_ENVVAR,
        help='The ID of a Threat Response API client.',
    )
    @click.option(
        '-p', '--client_password',
        prompt='Client Password',
        envvar=CLIENT_PASSWORD_ENVVAR,
        hide_input=True,
        help='The password of a Threat Response API client.',
    )
    @click.option(
        '-f', '--settings_file',
        type=click.File('r'),
        default=SETTINGS_FILE_DEFAULT,
        help='The path to a Relay settings file.',
    )
    def command(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            message = click.style(str(result), fg='green')
            click.echo(message)
            return result
        except Exception as exception:
            message = click.style(str(exception), fg='red')
            raise click.ClickException(message)

    relay.add_command(command)


@relay_command
def add(client_id, client_password, settings_file):
    tr = ThreatResponse(client_id, client_password)

    settings = load_settings(settings_file)

    modules = tr.int.module_instance.get()

    module = _module(modules, settings)
    if module:
        template = 'Relay module "{name}" already exists!'
        message = template.format(**settings)
        raise ModuleAlreadyExistsError(message)

    tr.int.module_instance.post(settings)

    template = 'Relay module "{name}" has been successfully added!'
    return template.format(**settings)


@relay_command
def edit(client_id, client_password, settings_file):
    tr = ThreatResponse(client_id, client_password)

    settings = load_settings(settings_file)

    modules = tr.int.module_instance.get()

    module = _module(modules, settings)
    if not module:
        template = 'Relay module "{name}" does not exist!'
        message = template.format(**settings)
        raise ModuleDoesNotExistError(message)

    diff = _diff(module, settings)
    if not diff:
        template = 'Relay module "{name}" has not been changed!'
        message = template.format(**settings)
        raise ModuleHasNotBeenChangedError(message)

    tr.int.module_instance.patch(module['id'], diff)

    template = 'Relay module "{name}" has been successfully edited!'
    return template.format(**settings)


@relay_command
def remove(client_id, client_password, settings_file):
    tr = ThreatResponse(client_id, client_password)

    settings = load_settings(settings_file)

    modules = tr.int.module_instance.get()

    module = _module(modules, settings)
    if not module:
        template = 'Relay module "{name}" does not exist!'
        message = template.format(**settings)
        raise ModuleDoesNotExistError(message)

    tr.int.module_instance.delete(module['id'])

    template = 'Relay module "{name}" has been successfully removed!'
    return template.format(**settings)


def _module(modules, settings):
    for module in modules:
        if (
            module['name'] == settings['name'] and
            module['module_type_id'] == settings['module_type_id']
        ):
            return module


def _diff(module, settings):
    return {
        key: value
        for key, value in settings.items()
        if module[key] != value
    }


def main():
    relay()


if __name__ == '__main__':
    main()
