"""TODO: add documentation."""

from __future__ import annotations

from importlib import metadata
from importlib.metadata import PackageNotFoundError
from typing import Any


def __getattr__(name: str) -> Any:
    if name == "__version__":
        try:
            return metadata.version("jmeter_test_suite")
        except PackageNotFoundError:
            try:
                from . import _version

                return _version.version
            except ImportError as exc:
                raise AttributeError(
                    f"module {__name__!r} has no attribute {name!r}"
                ) from exc
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["__version__"]
