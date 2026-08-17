from __future__ import annotations

from math import isqrt

import questionary
from pydantic import BaseModel, Field, ValidationError, field_validator
from questionary import Choice, Style

PLAIN_STYLE = Style(
    [
        ("qmark", "fg:default bold"),
        ("question", "fg:default"),
        ("answer", "fg:default bold"),
        ("pointer", "fg:default bold"),
        ("highlighted", "fg:default bold"),
        ("selected", "fg:default"),
    ]
)

LABELS = {
    "p": "p - nombre premier de la courbe",
    "a": "a - coefficient de la courbe",
    "b": "b - coefficient de la courbe",
    "dA": "dA - clé privée d'Alice",
    "dB": "dB - clé privée de Bob",
    "block_size": "taille de bloc en octets",
    "message": "texte à chiffrer",
    "number": "nombre entier à chiffrer",
}
DEFAULTS = {
    "p": 23,
    "a": 1,
    "b": 1,
    "dA": 5,
    "dB": 7,
    "block_size": 4,
    "message": "BONJOUR",
    "number": 12345,
}

ERROR_TYPES = {
    "int_parsing": "doit être un entier",
    "float_parsing": "doit être un nombre",
    "string_too_short": "doit contenir au moins {min_length} caractère(s)",
    "greater_than": "doit être strictement supérieur à {gt}",
    "greater_than_equal": "doit être supérieur ou égal à {ge}",
    "less_than": "doit être strictement inférieur à {lt}",
    "less_than_equal": "doit être inférieur ou égal à {le}",
    "missing": "est requis",
    "union_tag_invalid": "valeur invalide",
}


def is_prime(n: int) -> bool:
    return n > 1 and all(n % i for i in range(2, isqrt(n) + 1))


def french_error(error: dict) -> str:
    etype = error["type"]
    if etype == "value_error":
        return error["msg"].removeprefix("Value error, ")
    field = error["loc"][0] if error["loc"] else "saisie"
    label = LABELS.get(field, "saisie")
    template = ERROR_TYPES.get(etype)
    if template is None:
        return f"{label} : {error['msg']}"
    return f"{label} : {template.format(**(error.get('ctx') or {}))}"


class Config(BaseModel):
    dA: int = Field(gt=0, description="clé privée d'Alice")
    dB: int = Field(gt=0, description="clé privée de Bob")
    p: int = Field(default=23, gt=1, le=500, description="nombre premier de la courbe")
    a: int = Field(default=1, ge=0, description="coefficient de la courbe")
    b: int = Field(default=1, ge=0, description="coefficient de la courbe")
    block_size: int = Field(default=4, ge=1, description="taille de bloc en octets")
    message: str = Field(
        default="BONJOUR", min_length=1, description="texte à chiffrer"
    )
    number: int | None = Field(
        default=None, ge=0, description="nombre entier à chiffrer"
    )

    @field_validator("p")
    @classmethod
    def must_be_prime(cls, v: int) -> int:
        if not is_prime(v):
            raise ValueError("p doit être un nombre premier")
        return v


def ask_text(label: str, default: str = "", validate=None) -> str:
    value = questionary.text(
        label, default=default, validate=validate, style=PLAIN_STYLE
    ).ask()
    return value if value else default


def ask_confirm(message: str, default: bool = False) -> bool:
    return questionary.confirm(message, default=default, style=PLAIN_STYLE).ask()


def ask_select(message: str, choices: list[tuple[str, str]], default: str) -> str:
    return questionary.select(
        message,
        choices=[Choice(title, value) for title, value in choices],
        default=default,
        style=PLAIN_STYLE,
    ).ask()


def prompt_int(name: str) -> int:
    label = LABELS[name]
    default = DEFAULTS[name]
    while True:
        raw = ask_text(
            label,
            str(default),
            validate=lambda s: s == "" or s.isdigit() or "doit être un entier",
        )
        if raw == "":
            return default
        try:
            return int(raw)
        except ValueError:
            print(f"! {label} : doit être un entier")


def ask_payload() -> dict[str, str]:
    return {"message": ask_text(LABELS["message"], DEFAULTS["message"])}


def ask_config(payload: bool = True) -> Config:
    while True:
        values: dict[str, str | int] = {}
        for name in ("dA", "dB"):
            values[name] = prompt_int(name)
        if payload:
            values.update(ask_payload())
        if ask_confirm("Personnaliser p/a/b et la taille de bloc ?", default=False):
            for name in ("p", "a", "b", "block_size"):
                values[name] = prompt_int(name)
        try:
            return Config(**values)
        except ValidationError as exc:
            for error in exc.errors():
                print(f"! {french_error(error)}")
            print("Ressaisissez les valeurs.")
