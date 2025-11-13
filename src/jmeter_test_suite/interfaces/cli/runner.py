"""CLI runner for command-line interface entry point."""

import logging
import sys

from jmeter_test_suite.infrastructure.utils import (
    configure_logging,
    configure_windows_console,
)
from jmeter_test_suite.interfaces.cli.main import main
from jmeter_test_suite.interfaces.cli.utils import normalize_exit_code


def run_cli() -> int:
    """Run CLI application entry point.
    
    This function:
    1. Configures Windows console for UTF-8 encoding
    2. Configures application logging
    3. Invokes CLI main handler
    4. Normalizes and returns exit code
    
    Returns:
        Integer exit code: 0 for success, non-zero for failure
    """
    # Configure infrastructure: console and logging
    configure_windows_console()
    configure_logging()

    logger = logging.getLogger(__name__)
    try:
        result = main()
    except SystemExit as exc:
        # Allow nested sys.exit calls to propagate cleanly
        logger.debug("SystemExit raised inside CLI main", exc_info=exc)
        raise
    except Exception as exc:
        logger.exception("Uncaught exception in CLI main: %s", exc)
        return 1

    return normalize_exit_code(result)

