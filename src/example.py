from __future__ import annotations

from math import isqrt
from os import urandom

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


def number_to_bytes(n: int) -> bytes:
    """Convertit un entier en big-endian minimal d'octets (0 -> b'\\x00')."""
    if n < 0:
        raise ValueError("nombre négatif non supporté")
    return n.to_bytes((n.bit_length() + 7) // 8 or 1, byteorder="big")


def bytes_to_number(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big")


def ec_to_cbc_key(secret) -> int:
    return secret.x


def ask_payload() -> dict[str, str | int]:
    """Saisit le payload : un texte (t) ou un nombre entier (n)."""
    while True:
        choice = input("Chiffrer un texte (t) ou un nombre (n) [t] : ").strip().lower()
        if choice in ("", "t", "texte", "text"):
            raw = input(f"{LABELS['message']} [{DEFAULTS['message']}] : ").strip()
            return {"message": DEFAULTS["message"] if raw == "" else raw}
        if choice in ("n", "nombre", "number"):
            raw = input(f"{LABELS['number']} [{DEFAULTS['number']}] : ").strip()
            return {"number": DEFAULTS["number"] if raw == "" else raw}
        print("! saisie invalide : t (texte) ou n (nombre)")


def ask_advanced() -> bool:
    raw = (
        input("Personnaliser p/a/b et la taille de bloc ? (o/n) [n] : ").strip().lower()
    )
    return raw in ("o", "oui", "yes", "y")


def ask_config() -> Config:
    """3 saisies utiles (dA, dB, payload) ; p/a/b et taille de bloc en défauts modifiables."""
    while True:
        values: dict[str, str | int] = {}
        for name in ("dA", "dB"):
            raw = input(f"{LABELS[name]} [{DEFAULTS[name]}] : ").strip()
            values[name] = DEFAULTS[name] if raw == "" else raw
        values.update(ask_payload())
        if ask_advanced():
            for name in ("p", "a", "b", "block_size"):
                raw = input(f"{LABELS[name]} [{DEFAULTS[name]}] : ").strip()
                values[name] = DEFAULTS[name] if raw == "" else raw
        try:
            return Config(**values)
        except ValidationError as exc:
            for error in exc.errors():
                loc = error["loc"]
                label = LABELS[loc[0]] if loc else "p"
                print(f"! {label} : {error['msg']}")
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


def payload_bytes(cfg: Config) -> tuple[str, bytes]:
    """Retourne (type, octets du payload) : 'text' ou 'number'."""
    if cfg.number is not None:
        return "number", number_to_bytes(cfg.number)
    return "text", cfg.message.encode()


def main() -> None:
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
    print(f"IV  = {to_bin(iv)}")

    print("\n== Étape 7 : payload en blocs binaires ==")
    print(f"Payload binaire : {to_bin(payload)}")
    plain = pad(payload, cfg.block_size)
    blocks = split_blocks(plain, cfg.block_size)
    for i, block in enumerate(blocks, start=1):
        print(f"P_{i} = {to_bin(block)}")

    print("\n== Étape 8 : mode CBC ==")
    cipher = cbc_encrypt(blocks, key, iv)
    for i, block in enumerate(blocks, start=1):
        xored = xor_bytes(block, iv if i == 1 else cipher[i - 2])
        label = "P_1 XOR IV" if i == 1 else f"P_{i} XOR C_{i - 1}"
        print(f"{label} = {to_bin(xored)}")
        print(f"C_{i} = E_{key}(...) = {to_bin(cipher[i - 1])}")

    print("\n== Étape 9 : texte chiffré ==")
    ciphertext = b"".join(cipher)
    print(f"C = {to_bin(ciphertext)}")

    print("\n== Déchiffrement (vérification) ==")
    recovered = unpad(b"".join(cbc_decrypt(cipher, key, iv)))
    if payload_type == "number":
        print(f"Déchiffré : {bytes_to_number(recovered)} (doit être {cfg.number})")
    else:
        print(f"Déchiffré : {recovered!r} (doit être {cfg.message!r})")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"Erreur : {exc}")
