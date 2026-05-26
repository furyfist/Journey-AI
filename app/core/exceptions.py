class JourneyAIError(Exception):
    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.message
        super().__init__(self.message)


class ExternalAPIError(JourneyAIError):
    status_code = 502
    message = "External API failure"


class GroqAPIError(JourneyAIError):
    status_code = 502
    message = "LLM inference failure"


class SchemaValidationError(JourneyAIError):
    status_code = 500
    message = "AI output did not match expected schema"


class TripNotFoundError(JourneyAIError):
    status_code = 404
    message = "Trip not found"


class InvalidRegenerationTargetError(JourneyAIError):
    status_code = 400
    message = "Invalid regeneration target"


class RateLimitError(JourneyAIError):
    status_code = 429
    message = "Rate limit reached - please try again shortly"
