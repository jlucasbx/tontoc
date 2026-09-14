import sys

from tontoc.cli import run
from tontoc.lib import analyze


def main() -> None:
    sys.exit(run())


__all__ = [
    "analyze",
    "main",
]


if __name__ == "__main__":
    main()
