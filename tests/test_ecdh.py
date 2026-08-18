from src.ecc import ECCurve
from src.ecdh import keypair, shared_secret

CURVE = ECCurve(p=23, a=1, b=1)
GENERATOR = CURVE.point(3, 10)


def test_public_keys() -> None:
    _, alice_public = keypair(CURVE, GENERATOR, private=5)
    _, bob_public = keypair(CURVE, GENERATOR, private=7)
    assert alice_public == CURVE.point(9, 16)
    assert bob_public == CURVE.point(11, 3)


def test_shared_secret() -> None:
    _, alice_public = keypair(CURVE, GENERATOR, private=5)
    _, bob_public = keypair(CURVE, GENERATOR, private=7)
    alice_shared = shared_secret(CURVE, 5, bob_public)
    bob_shared = shared_secret(CURVE, 7, alice_public)
    assert alice_shared == bob_shared == CURVE.point(11, 3)


def test_cbc_key_is_x_coordinate() -> None:
    _, alice_public = keypair(CURVE, GENERATOR, private=5)
    _, bob_public = keypair(CURVE, GENERATOR, private=7)
    shared = shared_secret(CURVE, 5, bob_public)
    assert alice_public == CURVE.point(9, 16)
    assert shared.x == 11
