from __future__ import annotations

from math import isqrt
from os import urandom
from pathlib import Path

import questionary
from pydantic import BaseModel, Field, ValidationError, field_validator
from questionary import Choice, Style
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

HACK_THEME = Theme(
    {
        "frame": "#8f8f8f",
        "title": "#ffffff",
        "value": "#cfcfcf",
        "dim": "#6f6f6f",
        "alert": "bold white",
    }
)
console = Console(theme=HACK_THEME, style="white")

PROMPT_STYLE = Style(
    [
        ("qmark", "fg:#ffffff bold"),
        ("question", "fg:#cfcfcf"),
        ("answer", "fg:#ffffff bold"),
        ("pointer", "fg:#ffffff bold"),
        ("highlighted", "fg:#ffffff bold"),
        ("selected", "fg:#cfcfcf"),
    ]
)


def hack_panel(title: str, body: str) -> Panel:
    """Cadre façon outil de hacking : bordure grise, titre blanc."""
    return Panel(
        body,
        title=f"[bold title]{title}[/bold title]",
        border_style="frame",
        box=box.HEAVY,
    )


def banner() -> Panel:
    return Panel(
        "[value]ECC[/value] [dim]+[/dim] [value]ECDH[/value] "
        "[dim]+[/dim] [value]CBC[/value]\n"
        "[dim]chiffrez vos secrets[/dim]",
        title="[bold title] ECC-CBC [/bold title]",
        border_style="frame",
        box=box.DOUBLE,
    )


from cbc import cbc_decrypt, cbc_encrypt, pad, split_blocks, unpad, xor_bytes
from ecc import ECCurve, ECPoint
from ecdh import keypair, shared_secret


class Config(BaseModel):
    """dA, dB et le payload sont saisis ; le reste a des défauts modifiables."""

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


def is_prime(n: int) -> bool:
    return n > 1 and all(n % i for i in range(2, isqrt(n) + 1))


def to_bin(data: bytes) -> str:
    return " ".join(f"{b:08b}" for b in data)


def from_bin(binary_text: str) -> bytes:
    """Inverse de `to_bin` : un texte binaire (ex. "00001110 10010110") vers des octets."""
    return bytes(int(b, 2) for b in binary_text.split())


def load_binary(path: Path) -> bytes:
    """Lit un fichier de `output/` au format de `to_bin` et le convertit en octets."""
    return from_bin(path.read_text().strip())


OUT = Path("output")


def save_binary(name: str, content: str) -> Path:
    """Écrit le binaire lisible dans output/ et retourne son chemin."""
    OUT.mkdir(exist_ok=True)
    path = OUT / f"{name}.txt"
    path.write_text(content + "\n", encoding="utf-8")
    return path


def number_to_bytes(n: int) -> bytes:
    """Convertit un entier en big-endian minimal d'octets (0 -> b'\\x00')."""
    if n < 0:
        raise ValueError("nombre négatif non supporté")
    return n.to_bytes((n.bit_length() + 7) // 8 or 1, byteorder="big")


def bytes_to_number(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big")


def ec_to_cbc_key(secret) -> int:
    return secret.x


def prompt_int(name: str) -> int:
    """Saisit un entier validé en direct ; la boucle ne sert qu'au filet de sécurité."""
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
            console.print(f"[alert]![/alert] {label} : doit être un entier")


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


def french_error(error: dict) -> str:
    """Traduit une erreur pydantic en message français."""
    etype = error["type"]
    if etype == "value_error":
        return error["msg"].removeprefix("Value error, ")
    field = error["loc"][0] if error["loc"] else "saisie"
    label = LABELS.get(field, "saisie")
    template = ERROR_TYPES.get(etype)
    if template is None:
        return f"{label} : {error['msg']}"
    return f"{label} : {template.format(**(error.get('ctx') or {}))}"


def ask_text(label: str, default: str = "", validate=None) -> str:
    """Saisie questionary ; entrée vide ou Ctrl+C -> valeur par défaut."""
    value = questionary.text(
        label, default=default, validate=validate, style=PROMPT_STYLE
    ).ask()
    return value if value else default


def ask_confirm(message: str, default: bool = False) -> bool:
    return questionary.confirm(message, default=default, style=PROMPT_STYLE).ask()


def ask_select(message: str, choices: list[tuple[str, str]], default: str) -> str:
    return questionary.select(
        message,
        choices=[Choice(title, value) for title, value in choices],
        default=default,
        style=PROMPT_STYLE,
    ).ask()


def ask_payload() -> dict[str, str]:
    """Saisit le texte libre : lettres, chiffres, caractères spéciaux, espaces compris."""
    return {"message": ask_text(LABELS["message"], DEFAULTS["message"])}


def ask_config(payload: bool = True) -> Config:
    """Saisit la config ; `payload=False` saute la question du texte (mode déchiffrement)."""
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
                console.print(f"[alert]![/alert] {french_error(error)}")
            console.print("Ressaisissez les valeurs.")


def order(point: ECPoint) -> int:
    """Plus petit n > 0 tel que n·point = O (point à l'infini)."""
    n, acc = 0, None
    while True:
        if n and acc is None:
            return n
        acc = point.curve.add(acc, point)
        n += 1


def find_generator(curve: ECCurve, dA: int, dB: int) -> ECPoint:
    """Cherche le premier point sur la courbe dont l'ordre dépasse dA et dB."""
    # ponytail: scan O(p²), instantané pour p <= 500 ; passer à Tonelli-Shanks pour de grands p.
    for x in range(curve.p):
        rhs = (x**3 + curve.a * x + curve.b) % curve.p
        y = next((c for c in range(curve.p) if c * c % curve.p == rhs), None)
        if y is None:
            continue
        candidate = curve.point(x, y)
        if order(candidate) > max(dA, dB):
            return candidate
    raise ValueError("aucun point d'ordre > max(dA, dB) trouvé sur cette courbe")


def decrypt_files(cfg: Config) -> bytes:
    """Déchiffre output/ciphertext.txt : clé dérivée de l'ECDH, IV lu depuis output/iv.txt."""
    curve = ECCurve(p=cfg.p, a=cfg.a, b=cfg.b)
    generator = find_generator(curve, cfg.dA, cfg.dB)
    _, bob_public = keypair(curve, generator, private=cfg.dB)
    key = shared_secret(curve, private=cfg.dA, peer_public=bob_public).x
    iv = load_binary(OUT / "iv.txt")
    ciphertext = load_binary(OUT / "ciphertext.txt")
    return unpad(
        b"".join(cbc_decrypt(split_blocks(ciphertext, cfg.block_size), key, iv))
    )


def payload_bytes(cfg: Config) -> tuple[str, bytes]:
    """Retourne (type, octets du payload) : 'text' ou 'number'."""
    if cfg.number is not None:
        return "number", number_to_bytes(cfg.number)
    return "text", cfg.message.encode()


def main() -> None:
    console.print(banner())
    mode = ask_select(
        "Que voulez-vous faire ?",
        choices=[("Chiffrer", "c"), ("Déchiffrer", "d")],
        default="c",
    )
    if mode == "d":
        cfg = ask_config(payload=False)
        plain = decrypt_files(cfg)
        try:
            readable = plain.decode()
        except UnicodeDecodeError:
            readable = str(bytes_to_number(plain))
        OUT.mkdir(exist_ok=True)
        path = OUT / "plain.txt"
        path.write_text(readable + "\n", encoding="utf-8")
        console.print(
            hack_panel("DÉCHIFFRÉ", f"{readable}\nClair -> [value]{path}[/value]")
        )
        return

    cfg = ask_config()
    payload_type, payload = payload_bytes(cfg)

    curve = ECCurve(p=cfg.p, a=cfg.a, b=cfg.b)
    generator = find_generator(curve, cfg.dA, cfg.dB)
    console.print(
        hack_panel(
            "ÉTAPE 1/2 · COURBE ET GÉNÉRATEUR",
            f"{curve} avec G = [value]{generator}[/value]",
        )
    )

    _, alice_public = keypair(curve, generator, private=cfg.dA)
    _, bob_public = keypair(curve, generator, private=cfg.dB)
    console.print(
        hack_panel(
            "ÉTAPE 3/4 · CLÉS PRIVÉES ET PUBLIQUES",
            f"Q_A = {cfg.dA}G = [value]{alice_public}[/value]\n"
            f"Q_B = {cfg.dB}G = [value]{bob_public}[/value]",
        )
    )

    alice_shared = shared_secret(curve, private=cfg.dA, peer_public=bob_public)
    bob_shared = shared_secret(curve, private=cfg.dB, peer_public=alice_public)
    assert alice_shared == bob_shared
    console.print(
        hack_panel(
            "ÉTAPE 5 · ECDH -> POINT PARTAGÉ", f"K = [value]{alice_shared}[/value]"
        )
    )

    key = ec_to_cbc_key(alice_shared)
    iv = urandom(cfg.block_size)
    console.print(hack_panel("ÉTAPE 6 · CLÉ CBC ET IV", f"K_x = [value]{key}[/value]"))

    plain = pad(payload, cfg.block_size)
    blocks = split_blocks(plain, cfg.block_size)
    blocks_text = "\n".join(
        f"P_{i} = {to_bin(block)}" for i, block in enumerate(blocks, start=1)
    )
    console.print(
        hack_panel(
            "ÉTAPE 7 · PAYLOAD EN BLOCS BINAIRES",
            f"{len(blocks)} bloc(s) de {cfg.block_size} octets après padding PKCS#7",
        )
    )

    cipher = cbc_encrypt(blocks, key, iv)
    xors_text = "\n".join(
        f"P_{i} XOR {'IV' if i == 1 else f'C_{i - 1}'} = {to_bin(xor_bytes(block, iv if i == 1 else cipher[i - 2]))}"
        for i, block in enumerate(blocks, start=1)
    )
    ciphers_text = "\n".join(
        f"C_{i} = E_{key}(...) = {to_bin(block)}"
        for i, block in enumerate(cipher, start=1)
    )
    console.print(
        hack_panel(
            "ÉTAPE 8 · MODE CBC",
            f"{len(cipher)} bloc(s) chiffré(s) : C_i = E_K(P_i XOR C_{{i-1}})",
        )
    )

    ciphertext = b"".join(cipher)
    files = [
        ("IV binaire", save_binary("iv", to_bin(iv))),
        ("Payload binaire", save_binary("payload", to_bin(payload))),
        ("Blocs P_i (padding)", save_binary("blocks", blocks_text)),
        ("P_i XOR (CBC)", save_binary("xor", xors_text)),
        ("Blocs chiffrés C_i", save_binary("cipher_blocks", ciphers_text)),
        ("Texte chiffré C", save_binary("ciphertext", to_bin(ciphertext))),
    ]
    table = Table(
        title="[bold title] FICHIERS ÉCRITS DANS output/ [/bold title]",
        border_style="frame",
        header_style="title",
        box=box.HEAVY,
    )
    table.add_column("Contenu", style="white")
    table.add_column("Fichier", style="value")
    for label, path in files:
        table.add_row(label, str(path))
    console.print(table)

    recovered = unpad(b"".join(cbc_decrypt(cipher, key, iv)))
    if payload_type == "number":
        body = (
            f"Déchiffré : [value]{bytes_to_number(recovered)}[/value] "
            f"(doit être {cfg.number})"
        )
    else:
        body = f"Déchiffré : [value]{recovered!r}[/value] (doit être {cfg.message!r})"
    console.print(hack_panel("DÉCHIFFREMENT (VÉRIFICATION)", body))


if __name__ == "__main__":
    try:
        main()
    except EOFError:
        console.print("[alert]Saisie interrompue.[/alert]")
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[alert]Erreur :[/alert] {exc}")
