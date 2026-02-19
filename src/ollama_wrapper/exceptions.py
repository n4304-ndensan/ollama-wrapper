class OllamaWrapperError(Exception):
    pass


class InvalidJsonError(OllamaWrapperError):
    pass


class RateLimitError(OllamaWrapperError):
    pass


class VisionNotSupportedError(OllamaWrapperError):
    pass


class TransportError(OllamaWrapperError):
    pass
