from cbc import cbc_decrypt, cbc_encrypt, pad, split_blocks, unpad, xor_bytes
from ecc import ECCurve
from ecdh import keypair, shared_secret

CURVE = ECCurve(p=23, a=1, b=1)
GENERATOR = CURVE.point(3, 10)
IV = bytes([202, 117, 141, 83])
BLOCK_SIZE = 4


def to_bin(data: bytes) -> str:
    return " ".join(f"{b:08b}" for b in data)


def ec_to_cbc_key(secret) -> int:
    """Étape 6 : la coordonnée x du point partagé sert de clé symétrique."""
    return secret.x


def main() -> None:
    print("== Étape 1/2 : courbe et générateur ==")
    print(f"{CURVE} avec G = {GENERATOR}")

    print("\n== Étape 3/4 : clés privées et publiques ==")
    _, alice_public = keypair(CURVE, GENERATOR, private=5)
    _, bob_public = keypair(CURVE, GENERATOR, private=7)
    print(f"Q_A = 5G = {alice_public}")
    print(f"Q_B = 7G = {bob_public}")

    print("\n== Étape 5 : ECDH -> point partagé ==")
    alice_shared = shared_secret(CURVE, private=5, peer_public=bob_public)
    bob_shared = shared_secret(CURVE, private=7, peer_public=alice_public)
    assert alice_shared == bob_shared
    print(f"K = 5·Q_B = 7·Q_A = {alice_shared}")

    print("\n== Étape 6 : clé CBC ==")
    key = ec_to_cbc_key(alice_shared)
    print(f"K_x = {key}")

    print("\n== Étape 7 : texte en blocs binaires ==")
    plain = pad(b"BONJOUR", BLOCK_SIZE)
    blocks = split_blocks(plain, BLOCK_SIZE)
    print(f"P_1 = {to_bin(blocks[0])}")
    print(f"P_2 = {to_bin(blocks[1])}")

    print("\n== Étape 8 : mode CBC ==")
    print(f"IV  = {to_bin(IV)}")
    cipher = cbc_encrypt(blocks, key, IV)
    print(f"P_1 XOR IV = {to_bin(xor_bytes(blocks[0], IV))}")
    print(f"C_1 = E_{key}(P_1 XOR IV) = {to_bin(cipher[0])}")
    print(f"C_2 = E_{key}(P_2 XOR C_1) = {to_bin(cipher[1])}")

    print("\n== Étape 9 : texte chiffré ==")
    ciphertext = b"".join(cipher)
    print(f"C = C_1 || C_2 = {to_bin(ciphertext)}")

    print("\n== Déchiffrement (vérification) ==")
    recovered = unpad(b"".join(cbc_decrypt(cipher, key, IV)))
    print(f"Déchiffré : {recovered!r} (doit être b'BONJOUR')")


if __name__ == "__main__":
    main()
