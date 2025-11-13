"""CLI utilities for command-line interface layer."""

import logging
from typing import Any


def normalize_exit_code(value: Any) -> int:
    """Normalize CLI exit code to integer.
    
    Args:
        value: Exit code value from CLI command handler
        
    Returns:
        Integer exit code: 0 for success, 1 for failure
    """
    if value is None:
        return 0
    if isinstance(value, int):
        return value

    logger = logging.getLogger(__name__)
    logger.warning(
        "CLI main returned a non-integer exit code; defaulting to 1."
    )
    return 1

