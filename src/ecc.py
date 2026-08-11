from __future__ import annotations


class ECPoint:
    """Un point de la courbe elliptique E : y² = x³ + a·x + b (mod p)."""

    def __init__(self, curve: ECCurve, x: int, y: int) -> None:
        if not curve.is_on_curve(x, y):
            raise ValueError(f"({x}, {y}) n'est pas sur la courbe {curve}")
        self.curve = curve
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ECPoint):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __add__(self, other: ECPoint) -> ECPoint | None:
        return self.curve.add(self, other)

    def __sub__(self, other: ECPoint) -> ECPoint | None:
        return self.curve.add(self, self.curve.neg(other))

    def __neg__(self) -> ECPoint:
        return self.curve.neg(self)

    def __rmul__(self, k: int) -> ECPoint | None:
        return self.curve.mul(k, self)


class ECCurve:
    """Courbe elliptique E : y² = x³ + a·x + b sur le corps fini F_p."""

    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a % p
        self.b = b % p

    def __repr__(self) -> str:
        return f"ECC(p={self.p}, a={self.a}, b={self.b})"

    def point(self, x: int, y: int) -> ECPoint:
        return ECPoint(self, x % self.p, y % self.p)

    def is_on_curve(self, x: int, y: int) -> bool:
        return (y * y - (x**3 + self.a * x + self.b)) % self.p == 0

    def neg(self, p: ECPoint) -> ECPoint:
        return ECPoint(self, p.x, (-p.y) % self.p)

    def add(self, p1: ECPoint | None, p2: ECPoint | None) -> ECPoint | None:
        """Addition de points P1 + P2. Le point à l'infini est `None`."""
        if p1 is None:
            return p2
        if p2 is None:
            return p1
        if p1.x == p2.x and (p1.y + p2.y) % self.p == 0:
            return None
        if p1 == p2:
            lam = ((3 * p1.x * p1.x + self.a) * pow(2 * p1.y, -1, self.p)) % self.p
        else:
            lam = ((p2.y - p1.y) * pow(p2.x - p1.x, -1, self.p)) % self.p
        x3 = (lam * lam - p1.x - p2.x) % self.p
        y3 = (lam * (p1.x - x3) - p1.y) % self.p
        return ECPoint(self, x3, y3)

    def double(self, p: ECPoint) -> ECPoint | None:
        return self.add(p, p)

    def mul(self, k: int, p: ECPoint) -> ECPoint | None:
        """Multiplication scalaire k·P par doublement-et-addition (O(log k))."""
        result: ECPoint | None = None
        addend: ECPoint | None = p
        while k:
            if k & 1:
                result = self.add(result, addend)
            addend = self.double(addend)
            k >>= 1
        return result
