from ply.lex import Lexer as PlyLexer
from ply.lex import LexToken


class Token(LexToken):
    type: str
    value: str
    lineno: int
    lexpos: int
    lexer: PlyLexer
    column: int
