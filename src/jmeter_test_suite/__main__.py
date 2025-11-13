"""CLI entry point module for jmeter_test_suite package."""

from __future__ import annotations

import sys

from jmeter_test_suite.interfaces.cli.runner import run_cli


if __name__ == "__main__":
    sys.exit(run_cli())
