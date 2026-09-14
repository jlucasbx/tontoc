import sys

from tontoc.args import Args
from tontoc.colors import Style
from tontoc.lib import analyze
from tontoc.reader import read_file


def handle_analyze(args: Args) -> int:
    color_enabled = not args.no_color
    try:
        source_code = read_file(args.source_file)
    except (FileNotFoundError, IsADirectoryError) as err:
        prefix = Style.BOLD("error:", Style.BRIGHT_RED, enabled=sys.stderr.isatty() and color_enabled)
        print(f"{prefix} {err}", file=sys.stderr)
        return 1

    reporter = analyze(source_code, color=sys.stdout.isatty() and color_enabled)
    print(reporter.report())
    if reporter.lexer.errors:
        return 1
    return 0


def run(argv: list[str] | None = None) -> int:
    args = Args(argv)
    return handle_analyze(args)
