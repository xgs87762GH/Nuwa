

class Result:
    def __init__(self, is_success: bool, value=None, error: Exception = None):
        self.is_success = is_success
        self.value = value
        self.error = error

    @staticmethod
    def ok(value=None):
        return Result(True, value=value)

    @staticmethod
    def fail(error: Exception):
        return Result(False, error=error)

    def __repr__(self):
        if self.is_success:
            return f"Result(success, value={self.value})"
        else:
            return f"Result(failure, error={self.error})"
