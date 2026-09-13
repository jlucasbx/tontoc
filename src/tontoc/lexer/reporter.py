from tontoc.colors import Style
from tontoc.lexer.errors import LexicalError


class LexerReporter:
    def __init__(self, lexer, color: bool = True):
        self.lexer = lexer
        self.color = color

    def _resolve_color(self, color: bool | None) -> bool:
        return self.color if color is None else color

    def report(self, color: bool | None = None) -> str:
        c = self._resolve_color(color)
        sections = [self.tokens_report(color=c), self.summary_report(color=c)]
        if self.lexer.errors:
            sections.append(self.errors_report(color=c))
        return "\n".join(sections)

    @staticmethod
    def _token_style(t_type: str) -> tuple[Style, ...]:
        if t_type == "CLASS_ID":
            return (Style.BOLD, Style.BRIGHT_BLUE)
        if t_type == "RELATION_ID":
            return (Style.YELLOW,)
        if t_type == "INSTANCE_ID":
            return (Style.BOLD, Style.BRIGHT_YELLOW)
        if t_type == "CUSTOM_DATA_TYPE":
            return (Style.GREEN,)
        if t_type.startswith("TYPE_"):
            return (Style.BRIGHT_GREEN,)
        if t_type.startswith("KW_"):
            return (Style.BOLD, Style.BRIGHT_MAGENTA)
        if t_type.startswith("ST_"):
            return (Style.BRIGHT_CYAN,)
        if t_type.startswith("META_"):
            return (Style.MAGENTA,)
        return (Style.DIM,)

    def tokens_report(self, color: bool | None = None) -> str:
        c = self._resolve_color(color)
        lines = [
            Style.BOLD(
                "--- Visão Analítica dos Tokens ---\n", Style.BRIGHT_CYAN, enabled=c
            ),
            Style.BOLD(
                f"{'Line':<6} {'Col':<6} {'Token Type':<26} {'Lexeme/Value'}", enabled=c
            ),
            Style.DIM("-" * 60, enabled=c),
        ]
        for tok in self.lexer.get_tokens():
            col = getattr(tok, "column", tok.lexpos)
            line_str = Style.DIM(f"{tok.lineno:<6}", enabled=c)
            col_str = Style.DIM(f"{col:<6}", enabled=c)
            styles = self._token_style(tok.type)
            type_str = styles[0](f"{tok.type:<26}", *styles[1:], enabled=c)
            lines.append(f"{line_str} {col_str} {type_str} {tok.value}")
        return "\n".join(lines)

    @staticmethod
    def format_error(err: LexicalError, color: bool = True) -> str:
        return err.format(color=color)

    def errors_report(self, color: bool | None = None) -> str:
        if not self.lexer.errors:
            return ""
        c = self._resolve_color(color)
        lines = [
            Style.BOLD(
                "\n--- Lista de Erros e Sugestões ---\n", Style.BRIGHT_RED, enabled=c
            )
        ]
        for err in self.lexer.errors:
            lines.append(f"{self.format_error(err, color=c)}\n")
        return "\n".join(lines)

    def summary(self):
        counts = {
            "classes": 0,
            "relations": 0,
            "instances": 0,
            "custom_types": 0,
            "keywords": 0,
            "reserved_words": 0,
            "stereotypes": 0,
            "native_types": 0,
            "meta_attributes": 0,
            "errors": len(self.lexer.errors),
        }
        for tok in self.lexer.get_tokens():
            t_type = tok.type
            if t_type == "CLASS_ID":
                counts["classes"] += 1
            elif t_type == "RELATION_ID":
                counts["relations"] += 1
            elif t_type == "INSTANCE_ID":
                counts["instances"] += 1
            elif t_type == "CUSTOM_DATA_TYPE":
                counts["custom_types"] += 1
            elif t_type.startswith("KW_"):
                counts["reserved_words"] += 1
            elif t_type.startswith("ST_"):
                counts["stereotypes"] += 1
                counts["keywords"] += 1
            elif t_type.startswith("TYPE_"):
                counts["native_types"] += 1
            elif t_type.startswith("META_"):
                counts["meta_attributes"] += 1
        return counts

    def summary_report(self, color: bool | None = None) -> str:
        c = self._resolve_color(color)
        summary = self.summary()
        lines = [
            Style.BOLD(
                "\n--- Tabela de Síntese Estatística ---\n",
                Style.BRIGHT_CYAN,
                enabled=c,
            ),
            Style.BOLD(f"{'Categoria':<40} {'Quantidade':<10}", enabled=c),
            Style.DIM("-" * 52, enabled=c),
        ]
        items = [
            ("Classes (CLASS_ID)", summary["classes"]),
            ("Relações (RELATION_ID)", summary["relations"]),
            ("Palavras-chave / Estereótipos (ST_*)", summary["stereotypes"]),
            ("Indivíduos / Instâncias (INSTANCE_ID)", summary["instances"]),
            ("Palavras reservadas (KW_*)", summary["reserved_words"]),
            ("Meta-atributos (META_*)", summary["meta_attributes"]),
            ("Tipos Nativos (TYPE_*)", summary["native_types"]),
            ("Tipos Customizados (CUSTOM_DATA_TYPE)", summary["custom_types"]),
        ]
        for label, count in items:
            cat_str = f"{label:<40}"
            count_str = Style.BOLD(f"{count:<10}", Style.BRIGHT_YELLOW, enabled=c)
            lines.append(f"{cat_str} {count_str}")

        error_label = "Erros Léxicos"
        error_count = summary["errors"]
        if error_count > 0:
            err_line = Style.BOLD(
                f"{error_label:<40} {error_count:<10}", Style.BRIGHT_RED, enabled=c
            )
        else:
            cat_str = f"{error_label:<40}"
            count_str = Style.BOLD(f"{error_count:<10}", Style.BRIGHT_GREEN, enabled=c)
            err_line = f"{cat_str} {count_str}"
        lines.append(err_line)

        return "\n".join(lines)
