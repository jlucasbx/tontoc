from tontoc.colors import Style


class LexicalError:
    def __init__(
        self,
        lineno: int,
        column: int,
        value: str,
        message: str | None = None,
        suggestion: str | None = None,
        source_code: str | None = None,
        source_line: str | None = None,
    ):
        self.lineno = lineno
        self.column = column
        self.value = value
        self.suggestion = suggestion
        self.source_code = source_code
        self.source_line = source_line
        if message is not None:
            self.message: str = message
        else:
            self._diagnose()
        if self.source_line is None and self.source_code is not None:
            self._extract_source_line()

    def _diagnose(self) -> None:
        val = self.value
        if "DataType" in val or "Data_Type" in val or "datatype" in val.lower():
            self.message = f"Tipo de dado customizado malformado '{val}'"
            if "_" in val:
                self.suggestion = "Novos tipos (DataType) não podem conter sublinhados."
            elif any(c.isdigit() for c in val):
                self.suggestion = "Novos tipos (DataType) não podem conter números."
            else:
                self.suggestion = (
                    "Novos tipos (DataType) devem iniciar com letra, sem números ou"
                    " sublinhados, e terminar com 'DataType'."
                )
        elif val.startswith("_") or val.endswith("_"):
            self.message = f"Identificador malformado '{val}'"
            self.suggestion = (
                "Identificadores não podem iniciar ou terminar com sublinhado."
            )
        elif "__" in val:
            self.message = f"Identificador malformado '{val}'"
            self.suggestion = (
                "Identificadores não podem conter sublinhados consecutivos."
            )
        elif val[0].isdigit():
            self.message = f"Identificador malformado '{val}'"
            self.suggestion = "Identificadores não podem iniciar com dígitos numéricos."
        elif any(c.isdigit() for c in val):
            self.message = f"Identificador malformado '{val}'"
            if val[0].isupper():
                self.suggestion = (
                    "Identificadores de classe não podem conter números. Se for uma"
                    " instância, use como indivíduo; se for classe, remova o dígito."
                )
            else:
                self.suggestion = "Identificadores de relação não podem conter números."
        elif val[0].isupper() and not val.endswith("Class"):
            self.message = f"Identificador malformado '{val}'"
            self.suggestion = (
                "Identificadores de classe devem terminar com o sufixo 'Class'."
            )
        else:
            self.message = f"Identificador malformado '{val}'"

    def _extract_source_line(self) -> None:
        if self.source_code is None:
            return
        lines = self.source_code.splitlines()
        if 1 <= self.lineno <= len(lines):
            self.source_line = lines[self.lineno - 1]

    def format(self, color: bool = False) -> str:
        error_prefix = Style.BOLD("error:", Style.BRIGHT_RED, enabled=color)
        message_text = Style.BOLD(self.message, enabled=color)
        arrow = Style.BOLD("-->", Style.CYAN, enabled=color)
        gutter_bar = Style.BOLD("|", Style.CYAN, enabled=color)

        lines = [
            f"{error_prefix} {message_text}",
            f"  {arrow} Linha {self.lineno}, Coluna {self.column}",
        ]
        gutter_width = max(len(str(self.lineno)), 1)
        empty_gutter = " " * gutter_width
        lines.append(f" {empty_gutter} {gutter_bar}")
        if self.source_line is not None:
            line_no_str = Style.BOLD(
                f"{self.lineno:>{gutter_width}}", Style.CYAN, enabled=color
            )
            lines.append(f" {line_no_str} {gutter_bar} {self.source_line}")
        caret_padding = " " * max(self.column - 1, 0)
        carets = Style.BOLD(
            "^" * max(len(self.value), 1), Style.BRIGHT_RED, enabled=color
        )
        lines.append(f" {empty_gutter} {gutter_bar} {caret_padding}{carets}")
        if self.suggestion:
            suggestion_prefix = Style.BOLD("= Sugestão:", Style.GREEN, enabled=color)
            lines.append(f" {empty_gutter} {suggestion_prefix} {self.suggestion}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.format()
