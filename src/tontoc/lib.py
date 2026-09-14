from tontoc.lexer import Lexer, LexerReporter


def analyze(source_code: str, color: bool = True) -> LexerReporter:
    return LexerReporter(Lexer(source_code), color=color)
