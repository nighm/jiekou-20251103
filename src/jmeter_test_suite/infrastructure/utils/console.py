"""Console utilities for Windows platform."""

import io
import sys
from typing import TextIO, cast


def configure_windows_console() -> None:
    """Configure Windows console to support UTF-8 encoding.
    
    This function:
    1. Sets console code page to UTF-8 (65001) using Windows API
    2. Wraps stdout/stderr streams with UTF-8 encoding
    3. Handles errors gracefully to ensure program continues even if configuration fails
    """
    if sys.platform != "win32":
        return

    try:
        import ctypes

        # Set console output code page to UTF-8
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        # If setting fails, continue with stream wrapping
        pass

    # Wrap stdout/stderr streams with UTF-8 encoding
    stdout_buffer = getattr(sys.stdout, "buffer", None)
    stderr_buffer = getattr(sys.stderr, "buffer", None)
    
    if stdout_buffer is not None:
        try:
            sys.stdout = cast(
                TextIO, 
                io.TextIOWrapper(stdout_buffer, encoding="utf-8", errors="replace")
            )
        except Exception:
            # If wrapping fails, continue with original stream
            pass
    
    if stderr_buffer is not None:
        try:
            sys.stderr = cast(
                TextIO, 
                io.TextIOWrapper(stderr_buffer, encoding="utf-8", errors="replace")
            )
        except Exception:
            # If wrapping fails, continue with original stream
            pass

