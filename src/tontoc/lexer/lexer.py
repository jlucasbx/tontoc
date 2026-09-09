from ply import lex

from tontoc.lexer.errors import LexicalError
from tontoc.lexer.rules import LexerRules
from tontoc.lexer.types import Token


class Lexer(LexerRules):
    def __init__(self, data: str | None = None):
        self._errors: list[LexicalError] = []
        self._tokens: list[Token] = []
        self._lexer = lex.lex(object=self)
        if data is not None:
            self.input(data)

    def _find_column(self, token: Token) -> int:
        last_cr = self._lexer.lexdata.rfind("\n", 0, token.lexpos)
        if last_cr < 0:
            return token.lexpos + 1
        return token.lexpos - last_cr

    def input(self, data: str) -> None:
        self._errors.clear()
        self._tokens.clear()
        self._lexer.lineno = 1
        self._lexer.input(data)
        while tok := self._lexer.token():
            tok.column = self._find_column(tok)
            self._tokens.append(tok)

    @property
    def errors(self) -> list[LexicalError]:
        return self._errors

    def get_tokens(self) -> list[Token]:
        return self._tokens

    def handle_malformed_identifier(self, t: Token) -> None:
        t.column = self._find_column(t)
        error = LexicalError(
            lineno=t.lineno,
            column=t.column,
            value=t.value,
            source_code=self._lexer.lexdata,
        )
        self._errors.append(error)

    def t_error(self, t: Token) -> None:
        col = self._find_column(t)
        error = LexicalError(
            lineno=t.lineno,
            column=col,
            value=t.value[0],
            message=f"Caractere ilegal '{t.value[0]}'",
            source_code=self._lexer.lexdata,
        )
        self._errors.append(error)
        self._lexer.skip(1)
