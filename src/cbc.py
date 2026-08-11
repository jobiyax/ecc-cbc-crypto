from __future__ import annotations

FILL_BYTE = 0x58


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR bit à bit de deux blocs de même taille."""
    return bytes(x ^ y for x, y in zip(a, b))


def split_blocks(data: bytes, block_size: int) -> list[bytes]:
    """Découpe des octets en blocs de taille `block_size`."""
    return [data[i : i + block_size] for i in range(0, len(data), block_size)]


def pad(data: bytes, block_size: int) -> bytes:
    """Complète le dernier bloc avec le caractère de remplissage 'X' (comme la doc)."""
    pad_len = block_size - len(data) % block_size
    return data + bytes([FILL_BYTE]) * pad_len


def unpad(data: bytes) -> bytes:
    """Retire le remplissage 'X' de fin."""
    return data.rstrip(bytes([FILL_BYTE]))


def encrypt_block(key: int, block: bytes) -> bytes:
    """Fonction de chiffrement E_K : décalage de chaque octet de +K (mod 256)."""
    return bytes((b + key) % 256 for b in block)


def decrypt_block(key: int, block: bytes) -> bytes:
    """Inverse de E_K : décalage de chaque octet de -K (mod 256)."""
    return bytes((b - key) % 256 for b in block)


def cbc_encrypt(blocks: list[bytes], key: int, iv: bytes) -> list[bytes]:
    """C_i = E_K(P_i XOR C_{i-1}) avec C_0 = IV."""
    cipher: list[bytes] = []
    previous = iv
    for block in blocks:
        xored = xor_bytes(block, previous)
        current = encrypt_block(key, xored)
        cipher.append(current)
        previous = current
    return cipher


def cbc_decrypt(cipher: list[bytes], key: int, iv: bytes) -> list[bytes]:
    """P_i = D_K(C_i) XOR C_{i-1} avec C_0 = IV."""
    plain: list[bytes] = []
    previous = iv
    for block in cipher:
        decrypted = decrypt_block(key, block)
        plain.append(xor_bytes(decrypted, previous))
        previous = block
    return plain
