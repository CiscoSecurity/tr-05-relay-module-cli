class SettingsValidationError(ValueError):
    pass


class ModuleAlreadyExistsError(ValueError):
    pass


class ModuleDoesNotExistError(ValueError):
    pass


class ModuleHasNotBeenChangedError(ValueError):
    pass
