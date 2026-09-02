import argparse
import os


class Args:
    def __init__(self, argv: list[str] | None = None):
        parser = argparse.ArgumentParser(
            description="TONTO (Textual Ontology Language) lexical analyzer"
        )
        parser.add_argument("source_file", help="Path to the .tonto source file")
        parser.add_argument(
            "--no-color",
            action="store_true",
            help="Disable colored output",
        )
        args = parser.parse_args(argv)
        self.source_file: str = args.source_file
        self.no_color: bool = args.no_color or "NO_COLOR" in os.environ
