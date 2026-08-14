from __future__ import annotations

from math import isqrt
from os import urandom
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError, field_validator

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
    """Saisit un entier, relance tant que ce n'est pas un entier valide."""
    while True:
        raw = input(f"{LABELS[name]} [{DEFAULTS[name]}] : ").strip()
        if raw == "":
            return DEFAULTS[name]
        try:
            return int(raw)
        except ValueError:
            print(f"! {LABELS[name]} : doit être un entier")


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


def ask_payload() -> dict[str, str]:
    """Saisit le texte libre : lettres, chiffres, caractères spéciaux, espaces compris."""
    raw = input(f"{LABELS['message']} [{DEFAULTS['message']}] : ")
    return {"message": DEFAULTS["message"] if raw == "" else raw}


def ask_advanced() -> bool:
    raw = (
        input("Personnaliser p/a/b et la taille de bloc ? (o/n) [n] : ").strip().lower()
    )
    return raw in ("o", "oui", "yes", "y")


def ask_config(payload: bool = True) -> Config:
    """Saisit la config ; `payload=False` saute la question du texte (mode déchiffrement)."""
    while True:
        values: dict[str, str | int] = {}
        for name in ("dA", "dB"):
            values[name] = prompt_int(name)
        if payload:
            values.update(ask_payload())
        if ask_advanced():
            for name in ("p", "a", "b", "block_size"):
                values[name] = prompt_int(name)
        try:
            return Config(**values)
        except ValidationError as exc:
            for error in exc.errors():
                print(f"! {french_error(error)}")
            print("Ressaisissez les valeurs.")


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
    if input("Chiffrer (c) ou déchiffrer (d) ? [c] : ").strip().lower().startswith("d"):
        cfg = ask_config(payload=False)
        plain = decrypt_files(cfg)
        try:
            print(f"\nDéchiffré : {plain.decode()}")
        except UnicodeDecodeError:
            print(f"\nDéchiffré : {bytes_to_number(plain)}")
        return

    cfg = ask_config()
    payload_type, payload = payload_bytes(cfg)

    print("\n== Étape 1/2 : courbe et générateur (automatiques) ==")
    curve = ECCurve(p=cfg.p, a=cfg.a, b=cfg.b)
    generator = find_generator(curve, cfg.dA, cfg.dB)
    print(f"{curve} avec G = {generator}")

    print("\n== Étape 3/4 : clés privées et publiques ==")
    _, alice_public = keypair(curve, generator, private=cfg.dA)
    _, bob_public = keypair(curve, generator, private=cfg.dB)
    print(f"Q_A = {cfg.dA}G = {alice_public}")
    print(f"Q_B = {cfg.dB}G = {bob_public}")

    print("\n== Étape 5 : ECDH -> point partagé ==")
    alice_shared = shared_secret(curve, private=cfg.dA, peer_public=bob_public)
    bob_shared = shared_secret(curve, private=cfg.dB, peer_public=alice_public)
    assert alice_shared == bob_shared
    print(f"K = {alice_shared}")

    print("\n== Étape 6 : clé CBC et IV (automatiques) ==")
    key = ec_to_cbc_key(alice_shared)
    iv = urandom(cfg.block_size)
    print(f"K_x = {key}")
    print(f"IV  -> {save_binary('iv', to_bin(iv))}")

    print("\n== Étape 7 : payload en blocs binaires ==")
    print(f"Payload binaire -> {save_binary('payload', to_bin(payload))}")
    plain = pad(payload, cfg.block_size)
    blocks = split_blocks(plain, cfg.block_size)
    blocks_text = "\n".join(
        f"P_{i} = {to_bin(block)}" for i, block in enumerate(blocks, start=1)
    )
    print(f"Blocs P_i -> {save_binary('blocks', blocks_text)}")

    print("\n== Étape 8 : mode CBC ==")
    cipher = cbc_encrypt(blocks, key, iv)
    xors_text = "\n".join(
        f"P_{i} XOR {'IV' if i == 1 else f'C_{i - 1}'} = {to_bin(xor_bytes(block, iv if i == 1 else cipher[i - 2]))}"
        for i, block in enumerate(blocks, start=1)
    )
    ciphers_text = "\n".join(
        f"C_{i} = E_{key}(...) = {to_bin(block)}"
        for i, block in enumerate(cipher, start=1)
    )
    print(f"XOR -> {save_binary('xor', xors_text)}")
    print(f"C_i -> {save_binary('cipher_blocks', ciphers_text)}")

    print("\n== Étape 9 : texte chiffré ==")
    ciphertext = b"".join(cipher)
    print(f"C -> {save_binary('ciphertext', to_bin(ciphertext))}")

    print("\n== Déchiffrement (vérification) ==")
    recovered = unpad(b"".join(cbc_decrypt(cipher, key, iv)))
    if payload_type == "number":
        print(f"Déchiffré : {bytes_to_number(recovered)} (doit être {cfg.number})")
    else:
        print(f"Déchiffré : {recovered!r} (doit être {cfg.message!r})")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as exc:
        print(f"Erreur : {exc}")
