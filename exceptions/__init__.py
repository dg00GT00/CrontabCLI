class MinOutOfRangeException(Exception):
    """
    Exception to crontab minutes range
    """

    def __str__(self):
        return "The minutes field must be encompassed from 0 up to 59"


class NoCronEntryFound(Exception):
    """
    Exception to crontab minutes range
    """

    def __str__(self):
        return "The specified cron entry was not found"
