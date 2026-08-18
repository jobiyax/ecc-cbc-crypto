from __future__ import annotations

from pathlib import Path

from .ecc import ECCurve, ECPoint

OUT = Path("output")


def to_bin(data: bytes) -> str:
    return " ".join(f"{b:08b}" for b in data)


def from_bin(binary_text: str) -> bytes:
    return bytes(int(b, 2) for b in binary_text.split())


def load_binary(path: Path) -> bytes:
    return from_bin(path.read_text().strip())


def save_binary(name: str, content: str) -> Path:
    OUT.mkdir(exist_ok=True)
    path = OUT / f"{name}.txt"
    path.write_text(content + "\n", encoding="utf-8")
    return path


def number_to_bytes(n: int) -> bytes:
    if n < 0:
        raise ValueError("nombre négatif non supporté")
    return n.to_bytes((n.bit_length() + 7) // 8 or 1, byteorder="big")


def bytes_to_number(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big")


def ec_to_cbc_key(secret: ECPoint) -> int:
    return secret.x


def order(point: ECPoint) -> int:
    n, acc = 0, None
    while True:
        if n and acc is None:
            return n
        acc = point.curve.add(acc, point)
        n += 1


def find_generator(curve: ECCurve, dA: int, dB: int) -> ECPoint:
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
