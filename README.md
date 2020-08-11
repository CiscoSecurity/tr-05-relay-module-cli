[![Travis CI Build Status](https://travis-ci.com/CiscoSecurity/tr-05-relay-module-cli.svg?branch=develop)](https://travis-ci.com/CiscoSecurity/tr-05-relay-module-cli)

# Threat Response Relay Module CLI

Collection of useful Python CLI commands for managing Threat Response Relay
modules.

## Installation

* Local

```
pip install --upgrade .
pip show threatresponse-relay
```

* GitHub

```
pip install --upgrade git+https://github.com/CiscoSecurity/tr-05-relay-module-cli.git[@branch_name_or_release_version]
pip show threatresponse-relay
```

## Usage

* `relay --help`

```
Usage: relay [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add
  edit
  remove
```

* `relay add --help`

```
Usage: relay add [OPTIONS]

Options:
  -i, --client_id TEXT          The ID of a Threat Response API client.
  -p, --client_password TEXT    The password of a Threat Response API client.
  -f, --settings_file FILENAME  The path to a Relay settings file.
  --help                        Show this message and exit.
```

The command adds a new Relay module to Threat Response.

If a module with such a name already exists, then an error will be returned.

If the option `--client_id` is not specified, the command will try to read it
from the `TR_API_CLIENT_ID` environment variable. If that variable is also
not defined, then the command will prompt the user to enter some value directly
from the console.

The same rule applies to the `--client_password` option (the corresponding
environment variable is named `TR_API_CLIENT_PASSWORD`).

If the option `--settings_file` is not specified, the default value
`relay_settings.json` will be used. Check an example of
[relay_settings.json](relay_settings.json) to get more insight into how
such a file may look like.

Notice that in order not to hard-code any sensitive values to the file itself,
it is possible to use template strings instead of real values.
E.g.:
```json
{
  ...
  "name": "$NAME",
  ...
  "settings": {
    "url": "$URL",
    ...
  }
}
```
The actual values for `name` and `url` will be built based on the `NAME` and
`URL` environment variables respectively. If any of the environment variables
referred within the settings is not defined, then an error will be returned.
This is a very simplified version of shell parameter expansion/substitution.

**NOTE.** There is a convenient way of using the command by moving all the
necessary environment variables to some `.env` file and then reading them into
the child process (i.e. the actual command) environment prior to the execution.
E.g.:
```
env $(cat .env | xargs) relay add ...
```
It is also possible to use `export` instead of `env`, but the latter one allows
not to clutter the parent process environment with redundant variables.
E.g.:
```
export $(cat .env | xargs) && relay add ...
```
When in doubt, prefer `env` to `export` anyway.

* `relay edit --help`

```
Usage: relay edit [OPTIONS]

Options:
  -i, --client_id TEXT          The ID of a Threat Response API client.
  -p, --client_password TEXT    The password of a Threat Response API client.
  -f, --settings_file FILENAME  The path to a Relay settings file.
  --help                        Show this message and exit.
```

The command edits an existing Relay module in Threat Response.

If a module with such a name does not exist, then an error will be returned.

The meaning and behavior of all the options are the same as for `add`.

**NOTE.** The command uses the name of a module to search for it. So currently
it is not possible to edit the name of the module, only the other properties.
In order to rename the module it is possible to use the combination of `remove`
(with the old name) followed by `add` (with the new name) as a workaround.

* `relay remove --help`

```
Usage: relay remove [OPTIONS]

Options:
  -i, --client_id TEXT          The ID of a Threat Response API client.
  -p, --client_password TEXT    The password of a Threat Response API client.
  -f, --settings_file FILENAME  The path to a Relay settings file.
  --help                        Show this message and exit.
```

The command removes an existing Relay module from Threat Response.

If a module with such a name does not exist, then an error will be returned.

The meaning and behavior of all the options are the same as for `add`.
