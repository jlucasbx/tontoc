from abc import ABC, abstractmethod
from typing import ClassVar

from tontoc.lexer.types import Token


# =============================================================================
# PALAVRAS RESERVADAS (trabalho-01.md)
# =============================================================================
class LexerRules(ABC):
    reserved: ClassVar[dict[str, str]] = {
        # -------------------------------------------------------------------------
        # Estereótipos de classe
        # event, situation, process, category, mixin, phaseMixin, roleMixin,
        # historicalRoleMixin, kind, collective, quantity, quality, mode,
        # intrisicMode, extrinsicMode, subkind, phase, role, historicalRole
        # -------------------------------------------------------------------------
        "event": "ST_EVENT",
        "situation": "ST_SITUATION",
        "process": "ST_PROCESS",
        "category": "ST_CATEGORY",
        "mixin": "ST_MIXIN",
        "phaseMixin": "ST_PHASE_MIXIN",
        "roleMixin": "ST_ROLE_MIXIN",
        "historicalRoleMixin": "ST_HISTORICAL_ROLE_MIXIN",
        "kind": "ST_KIND",
        "collective": "ST_COLLECTIVE",
        "quantity": "ST_QUANTITY",
        "quality": "ST_QUALITY",
        "mode": "ST_MODE",
        "intrisicMode": "ST_INTRISIC_MODE",
        "extrinsicMode": "ST_EXTRINSIC_MODE",
        "subkind": "ST_SUBKIND",
        "phase": "ST_PHASE",
        "role": "ST_ROLE",
        "historicalRole": "ST_HISTORICAL_ROLE",
        # -------------------------------------------------------------------------
        # Estereótipos de relações
        # material, derivation, comparative, mediation, characterization,
        # externalDependence, componentOf, memberOf, subCollectionOf, subQualityOf,
        # instantiation, termination, participational, participation,
        # historicalDependence, creation, manifestation, bringsAbout, triggers,
        # composition, aggregation, inherence, value, formal, constitution
        # -------------------------------------------------------------------------
        "material": "ST_MATERIAL",
        "derivation": "ST_DERIVATION",
        "comparative": "ST_COMPARATIVE",
        "mediation": "ST_MEDIATION",
        "characterization": "ST_CHARACTERIZATION",
        "externalDependence": "ST_EXTERNAL_DEPENDENCE",
        "componentOf": "ST_COMPONENT_OF",
        "memberOf": "ST_MEMBER_OF",
        "subCollectionOf": "ST_SUB_COLLECTION_OF",
        "subQualityOf": "ST_SUB_QUALITY_OF",
        "instantiation": "ST_INSTANTIATION",
        "termination": "ST_TERMINATION",
        "participational": "ST_PARTICIPATIONAL",
        "participation": "ST_PARTICIPATION",
        "historicalDependence": "ST_HISTORICAL_DEPENDENCE",
        "creation": "ST_CREATION",
        "manifestation": "ST_MANIFESTATION",
        "bringsAbout": "ST_BRINGS_ABOUT",
        "triggers": "ST_TRIGGERS",
        "composition": "ST_COMPOSITION",
        "aggregation": "ST_AGGREGATION",
        "inherence": "ST_INHERENCE",
        "value": "ST_VALUE",
        "formal": "ST_FORMAL",
        "constitution": "ST_CONSTITUTION",
        # -------------------------------------------------------------------------
        # Palavras reservadas / Palavras-chave
        # genset, disjoint, complete, general, specifics, where, package, import
        # -------------------------------------------------------------------------
        "genset": "KW_GENSET",
        "disjoint": "KW_DISJOINT",
        "complete": "KW_COMPLETE",
        "general": "KW_GENERAL",
        "specifics": "KW_SPECIFICS",
        "where": "KW_WHERE",
        "package": "KW_PACKAGE",
        "import": "KW_IMPORT",
        "relation": "KW_RELATION",
        # -------------------------------------------------------------------------
        # Tipos de dados nativos
        # number, string, boolean, date, time, datetime
        # -------------------------------------------------------------------------
        "number": "TYPE_NUMBER",
        "string": "TYPE_STRING",
        "boolean": "TYPE_BOOLEAN",
        "date": "TYPE_DATE",
        "time": "TYPE_TIME",
        "datetime": "TYPE_DATETIME",
        # -------------------------------------------------------------------------
        # Meta-atributos
        # ordered, const, derived, subsets, redefines
        # -------------------------------------------------------------------------
        "ordered": "META_ORDERED",
        "const": "META_CONST",
        "derived": "META_DERIVED",
        "subsets": "META_SUBSETS",
        "redefines": "META_REDEFINES",
    }

    # =============================================================================
    # LISTA DE TOKENS (PLY)
    # =============================================================================
    tokens: ClassVar[list[str]] = [
        # Palavra reservada com hífen
        "KW_FUNCTIONAL_COMPLEXES",
        # Identificadores e tipos customizados
        "CUSTOM_DATA_TYPE",
        "INSTANCE_ID",
        "CLASS_ID",
        "RELATION_ID",
        # Símbolos especiais e operadores de agregação
        "LBRACE",
        "RBRACE",
        "LPAREN",
        "RPAREN",
        "LBRACKET",
        "RBRACKET",
        "DOTDOT",
        "DOT",
        "COMMA",
        "LINK",
        "AGGREGATION_LEFT",
        "AGGREGATION_RIGHT",
        "SHARED_AGGREGATION_LEFT",
        "SHARED_AGGREGATION_RIGHT",
        "ASTERISK",
        "AT",
        "COLON",
        "INT",
    ] + list(reserved.values())

    # =============================================================================
    # REGRAS PARA PALAVRAS RESERVADAS ESPECIAIS
    # =============================================================================
    def t_KW_FUNCTIONAL_COMPLEXES(self, t: Token) -> Token:
        r"functional-complexes"
        return t

    # =============================================================================
    # SÍMBOLOS ESPECIAIS (trabalho-01.md e especificação oficial TONTO)
    # “{“, “}”, “(“, “)”, “[“, “]”, “..”, “.”, “,”, “--”, “<>--”, “--<>”,
    # “<o>--”, “--<o>”, “*”, “@”, “:”
    # =============================================================================
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_DOTDOT = r"\.\."
    t_DOT = r"\."
    t_COMMA = r","
    t_SHARED_AGGREGATION_LEFT = r"<o>--"
    t_SHARED_AGGREGATION_RIGHT = r"--<o>"
    t_AGGREGATION_LEFT = r"<>--"
    t_AGGREGATION_RIGHT = r"--<>"
    t_LINK = r"--"
    t_ASTERISK = r"\*"
    t_AT = r"@"
    t_COLON = r":"

    # Caracteres ignorados (espaços e tabulações)
    t_ignore = " \t"

    # =============================================================================
    # IDENTIFICADORES E CONVENÇÕES DE NOMENCLATURA (trabalho-01.md)
    # =============================================================================

    # Novos tipos: iniciando com letra, sem números, sem sublinhado e terminando com "DataType"
    # Ex: CPFDataType, PhoneNumberDataType
    def t_CUSTOM_DATA_TYPE(self, t: Token) -> Token:
        r"[a-zA-Z]+DataType(?![a-zA-Z0-9_])"
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
        return t

    # Convenção para nomes de instâncias: iniciando com qualquer letra, podendo ter
    # sublinhado como subcadeia própria e terminando com algum número inteiro.
    # Ex: Planeta1, Planeta2, pizza03, pizza123
    def t_INSTANCE_ID(self, t: Token) -> Token:
        r"[a-zA-Z](?:[a-zA-Z0-9]|_(?=[a-zA-Z0-9]))*\d+(?![a-zA-Z0-9_])"
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
        return t

    # Convenção para nomes de classes: iniciando com letra maiúscula, seguida por
    # qualquer combinação de letras, ou tendo sublinhado como subcadeia própria, sem números.
    # Ex: Person, Child, Church, University, Second_Baptist_Church
    def t_CLASS_ID(self, t: Token) -> Token:
        r"[A-Z](?:[a-zA-Z]|_(?=[a-zA-Z]))*Class(?![a-zA-Z0-9_])"
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
        return t

    # Convenção para nomes de relações: começando com letra minúscula, seguida por
    # qualquer combinação de letras, ou tendo sublinhado como subcadeia própria, sem números.
    # Ex: has, hasParent, has_parent, isPartOf, is_part_of
    def t_RELATION_ID(self, t: Token) -> Token:
        r"[a-z](?:[a-zA-Z]|_(?=[a-zA-Z]))*(?![a-zA-Z0-9_])"
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
        return t

    def t_INT(self, t: Token) -> Token:
        r"\d+(?![a-zA-Z0-9_])"
        return t

    def t_MALFORMED_IDENTIFIER(self, t: Token) -> None:
        r"[a-zA-Z0-9_]+"
        self.handle_malformed_identifier(t)

    # =============================================================================
    # COMENTÁRIOS E CONTROLE DE LINHAS
    # =============================================================================

    # Comentários de linha única: //...
    def t_comment_single(self, _: Token) -> None:
        r"//.*"

    # Comentários de múltiplas linhas: /* ... */
    def t_comment_multi(self, t: Token) -> None:
        r"/\*(?:.|\n)*?\*/"
        t.lexer.lineno += t.value.count("\n")

    # Rastreamento de quebras de linha para atualização do número da linha
    def t_newline(self, t: Token) -> None:
        r"(?:\r?\n)+"
        t.lexer.lineno += t.value.count("\n")

    @abstractmethod
    def handle_malformed_identifier(self, t: Token) -> None:
        pass
