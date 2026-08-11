from cbc import (
    cbc_decrypt,
    cbc_encrypt,
    decrypt_block,
    encrypt_block,
    pad,
    split_blocks,
    unpad,
    xor_bytes,
)

KEY = 11
IV = bytes([202, 117, 141, 83])


def test_xor_bytes() -> None:
    assert xor_bytes(bytes([0b10101010]), bytes([0b11001100])) == bytes([0b01100110])


def test_xor_first_block_with_iv_matches_doc() -> None:
    p1 = bytes([66, 79, 78, 74])
    assert xor_bytes(p1, IV) == bytes([136, 58, 195, 25])


def test_pad_and_split() -> None:
    padded = pad(b"BONJOUR", 4)
    assert padded == b"BONJOUR\x01"
    assert split_blocks(padded, 4) == [b"BONJ", b"OUR\x01"]
    assert unpad(padded) == b"BONJOUR"


def test_pad_full_block_adds_whole_extra_block() -> None:
    padded = pad(b"BONJ", 4)
    assert padded == b"BONJ\x04\x04\x04\x04"
    assert unpad(padded) == b"BONJ"


def test_pad_keeps_trailing_x_byte() -> None:
    assert unpad(pad(b"HELLO X", 4)) == b"HELLO X"


def test_shift_cipher_round_trip() -> None:
    block = bytes([66, 79, 78, 74])
    assert decrypt_block(KEY, encrypt_block(KEY, block)) == block
    assert encrypt_block(KEY, bytes([5])) == bytes([16])


def test_cbc_encrypt_decrypt_round_trip() -> None:
    plain = pad(b"BONJOUR", 4)
    blocks = split_blocks(plain, 4)
    cipher = cbc_encrypt(blocks, KEY, IV)
    assert len(cipher) == 2
    recovered = unpad(b"".join(cbc_decrypt(cipher, KEY, IV)))
    assert recovered == b"BONJOUR"


def test_cbc_chaining_makes_blocks_depend_on_previous() -> None:
    blocks = split_blocks(pad(b"BONJOUR", 4), 4)
    cipher = cbc_encrypt(blocks, KEY, IV)
    assert cipher[0] != cipher[1]


def test_same_plaintext_differs_with_iv() -> None:
    iv1 = IV
    iv2 = bytes([IV[0] ^ 1, *IV[1:]])
    assert cbc_encrypt([b"AAAA"], KEY, iv1)[0] != cbc_encrypt([b"AAAA"], KEY, iv2)[0]
