import re

import pytest
from pydantic import ValidationError

from cbc import cbc_decrypt, cbc_encrypt, pad, split_blocks, unpad
from ecc import ECCurve
from ecdh import keypair, shared_secret
from main import (
    Config,
    ask_config,
    bytes_to_number,
    find_generator,
    french_error,
    is_prime,
    number_to_bytes,
    order,
    payload_bytes,
)

ENGLISH = re.compile(
    r"\b(Input|Value error|greater|less|should|must|field|required)\b", re.IGNORECASE
)


def test_ask_config_retries_on_invalid_input(monkeypatch) -> None:
    answers = iter(["abc", "5", "7", "n", "xyz", "12345", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    cfg = ask_config()
    assert (cfg.dA, cfg.dB, cfg.number) == (5, 7, 12345)


def test_error_messages_are_french() -> None:
    cases = [
        {"p": 24, "a": 1, "b": 1, "dA": 5, "dB": 7},
        {"p": 501, "a": 1, "b": 1, "dA": 5, "dB": 7},
        {"p": 23, "a": 1, "b": 1, "dA": 0, "dB": 7},
        {"p": 23, "a": 1, "b": 1, "dA": 5, "dB": 7, "block_size": 0},
        {"p": 23, "a": 1, "b": 1, "dA": 5, "dB": 7, "number": -1},
        {"p": 23, "a": 1, "b": 1, "dA": 5, "dB": 7, "message": ""},
    ]
    for kwargs in cases:
        with pytest.raises(ValidationError) as exc:
            Config(**kwargs)
        msgs = [french_error(e) for e in exc.value.errors()]
        assert msgs, "aucune erreur produite"
        for msg in msgs:
            assert not ENGLISH.search(msg), f"message en anglais : {msg}"


def test_is_prime() -> None:
    assert is_prime(23)
    assert not is_prime(22)
    assert not is_prime(1)


def test_config_valid() -> None:
    cfg = Config(p=23, a=1, b=1, dA=5, dB=7, message="BONJOUR", block_size=4)
    assert cfg.p == 23


def test_config_defaults_are_doc_values() -> None:
    cfg = Config(dA=5, dB=7)
    assert (cfg.p, cfg.a, cfg.b, cfg.block_size) == (23, 1, 1, 4)
    assert cfg.message == "BONJOUR"


def test_config_rejects_non_prime_p() -> None:
    with pytest.raises(ValidationError):
        Config(p=22, a=1, b=1, dA=5, dB=7, message="B", block_size=4)


def test_config_rejects_zero_private_key() -> None:
    with pytest.raises(ValidationError):
        Config(p=23, a=1, b=1, dA=0, dB=7, message="B", block_size=4)


def test_config_rejects_empty_message() -> None:
    with pytest.raises(ValidationError):
        Config(p=23, a=1, b=1, dA=5, dB=7, message="", block_size=4)


def test_config_accepts_number_payload() -> None:
    cfg = Config(p=23, a=1, b=1, dA=5, dB=7, number=12345, block_size=4)
    assert payload_bytes(cfg) == ("number", b"09")


def test_config_rejects_negative_number() -> None:
    with pytest.raises(ValidationError):
        Config(p=23, a=1, b=1, dA=5, dB=7, number=-1, block_size=4)


def test_number_to_bytes_round_trip() -> None:
    for n in (0, 255, 256, 12345, 2**64 + 13):
        assert bytes_to_number(number_to_bytes(n)) == n


def test_number_pipeline_round_trip() -> None:
    curve = ECCurve(p=23, a=1, b=1)
    g = find_generator(curve, dA=5, dB=7)
    _, bob_public = keypair(curve, g, 7)
    shared = shared_secret(curve, 5, bob_public)
    iv = bytes([202, 117, 141, 83])
    plain = pad(number_to_bytes(12345), 4)
    cipher = cbc_encrypt(split_blocks(plain, 4), shared.x, iv)
    recovered = unpad(b"".join(cbc_decrypt(cipher, shared.x, iv)))
    assert bytes_to_number(recovered) == 12345


def test_order_of_generator_is_28() -> None:
    curve = ECCurve(p=23, a=1, b=1)
    assert order(curve.point(3, 10)) == 28


def test_find_generator_on_curve_with_enough_order() -> None:
    curve = ECCurve(p=23, a=1, b=1)
    g = find_generator(curve, dA=5, dB=7)
    assert curve.is_on_curve(g.x, g.y)
    assert order(g) > 7


def test_pipeline_round_trip() -> None:
    curve = ECCurve(p=23, a=1, b=1)
    g = find_generator(curve, dA=5, dB=7)
    _, alice_public = keypair(curve, g, 5)
    _, bob_public = keypair(curve, g, 7)
    shared = shared_secret(curve, 5, bob_public)
    assert alice_public == 5 * g
    iv = bytes([202, 117, 141, 83])
    plain = pad(b"BONJOUR", 4)
    cipher = cbc_encrypt(split_blocks(plain, 4), shared.x, iv)
    recovered = unpad(b"".join(cbc_decrypt(cipher, shared.x, iv)))
    assert recovered == b"BONJOUR"
