import pytest

from src.ecc import ECCurve

CURVE = ECCurve(p=23, a=1, b=1)
G = CURVE.point(3, 10)


def test_point_on_curve() -> None:
    assert G.x == 3 and G.y == 10


def test_invalid_point_raises() -> None:
    with pytest.raises(ValueError):
        CURVE.point(0, 0)


def test_negation() -> None:
    assert CURVE.neg(G) == CURVE.point(3, -10 % 23)
    assert G + CURVE.neg(G) is None


def test_multiples_of_generator() -> None:
    expected = {
        2: (7, 12),
        3: (19, 5),
        4: (17, 3),
        5: (9, 16),
        6: (12, 4),
        7: (11, 3),
    }
    for k, (x, y) in expected.items():
        assert k * G == CURVE.point(x, y), f"{k}G attendu = {x, y}"


def test_double_and_add_matches_repeated_addition() -> None:
    acc = None
    for k in range(1, 28):
        acc = CURVE.add(acc, G)
        assert CURVE.mul(k, G) == acc


def test_generator_order() -> None:
    assert 27 * G != None
    assert 28 * G is None


def test_reduction_mod_order() -> None:
    assert 35 * G == 7 * G == CURVE.point(11, 3)


def test_add_is_commutative() -> None:
    p = 5 * G
    q = 7 * G
    assert p + q == q + p
