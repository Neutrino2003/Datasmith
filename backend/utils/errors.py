class DatasmithError(Exception):
    status_code: int = 500
    message: str = "An error occurred"

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class ExtractionError(DatasmithError):
    status_code = 400


class AgentError(DatasmithError):
    status_code = 500


class ValidationError(DatasmithError):
    status_code = 422


class ConfigurationError(DatasmithError):
    status_code = 500

