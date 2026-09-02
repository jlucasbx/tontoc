from __future__ import annotations

from enum import StrEnum


class Style(StrEnum):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    def __call__(self, text: str, *others: Style, enabled: bool = True) -> str:
        if not enabled:
            return text
        prefix = "".join([str(self)] + [str(s) for s in others])
        return f"{prefix}{text}{Style.RESET}"
