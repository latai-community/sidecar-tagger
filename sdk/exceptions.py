"""
Title: Sidecar Engine Exceptions
Abstract: Defines a semantic hierarchy of exceptions for the Sidecar-tagger project.
Dependencies: None
LLM-Hints: Use these exceptions to replace string-based error reporting in SDK and Parsers.
"""

class SidecarException(Exception):
    """Base exception for all Sidecar-tagger related errors."""
    pass

class ParserError(SidecarException):
    """Raised when a specific file parser fails to extract content."""
    pass

class LLMClientError(SidecarException):
    """Raised when there is an issue communicating with the LLM provider (e.g. Gemini)."""
    pass

class CacheError(SidecarException):
    """Raised when the semantic cache (FastEmbed/ONNX) fails to generate or compare vectors."""
    pass

class ConfigurationError(SidecarException):
    """Raised when environment variables or project settings are missing/invalid."""
    pass
