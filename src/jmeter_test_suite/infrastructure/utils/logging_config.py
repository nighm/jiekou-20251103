"""Logging configuration utilities."""

import logging


def configure_logging() -> None:
    """Configure application logging.
    
    Sets up basic logging configuration with INFO level and standard format.
    Only configures if no handlers are already present to avoid duplicate configuration.
    """
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )

