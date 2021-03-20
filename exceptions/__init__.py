class MinOutOfRangeException(Exception):
    """
    Exception to crontab minutes range
    """

    def __str__(self) -> str:
        return "The minutes field must be encompassed from 0 up to 59"


class NoCronEntryFound(Exception):
    """
    Exception to crontab minutes range
    """

    def __str__(self) -> str:
        return "The specified cron entry was not found"


class NoPyModuleFound(Exception):
    """
    Exception when Python module is not found
    """

    def __str__(self) -> str:
        return "When --module, -m switch specified, the python module path and python module name should be determined"
