import datetime


class TimeUtils(object):
    """
    TimeUtils class provides utility methods for working with time.
    """

    @staticmethod
    def get_current_time() -> datetime:
        """
        Returns the current time.

        Returns:
            datetime: The current time.
        """
        return datetime.datetime.now(datetime.timezone.utc)
