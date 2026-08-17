from __future__ import annotations

from os import urandom

from cbc import cbc_decrypt, cbc_encrypt, pad, split_blocks, unpad, xor_bytes
from config import Config, ask_config, ask_select
from ecc import ECCurve
from ecdh import keypair, shared_secret
from utils import (
    OUT,
    bytes_to_number,
    ec_to_cbc_key,
    find_generator,
    load_binary,
    number_to_bytes,
    save_binary,
    to_bin,
)


def banner() -> str:
    return "ECC + ECDH + CBC — chiffrez vos secrets"


def step(title: str, body: str) -> None:
    print(f"\n== {title} ==")
    print(body)


def payload_bytes(cfg: Config) -> tuple[str, bytes]:
    if cfg.number is not None:
        return "number", number_to_bytes(cfg.number)
    return "text", cfg.message.encode()


def decrypt_files(cfg: Config) -> bytes:
    curve = ECCurve(p=cfg.p, a=cfg.a, b=cfg.b)
    generator = find_generator(curve, cfg.dA, cfg.dB)
    _, bob_public = keypair(curve, generator, private=cfg.dB)
    key = shared_secret(curve, private=cfg.dA, peer_public=bob_public).x
    iv = load_binary(OUT / "iv.txt")
    ciphertext = load_binary(OUT / "ciphertext.txt")
    return unpad(
        b"".join(cbc_decrypt(split_blocks(ciphertext, cfg.block_size), key, iv))
    )


def main() -> None:
    print(banner())
    mode = ask_select(
        "Que voulez-vous faire ?",
        choices=[("Chiffrer", "c"), ("Déchiffrer", "d")],
        default="c",
    )
    if mode == "d":
        cfg = ask_config(payload=False)
        plain = decrypt_files(cfg)
        try:
            readable = plain.decode()
        except UnicodeDecodeError:
            readable = str(bytes_to_number(plain))
        OUT.mkdir(exist_ok=True)
        path = OUT / "plain.txt"
        path.write_text(readable + "\n", encoding="utf-8")
        step("DÉCHIFFRÉ", f"{readable}\nClair -> {path}")
        return

    cfg = ask_config()
    payload_type, payload = payload_bytes(cfg)

    curve = ECCurve(p=cfg.p, a=cfg.a, b=cfg.b)
    generator = find_generator(curve, cfg.dA, cfg.dB)
    step("ÉTAPE 1/2 · COURBE ET GÉNÉRATEUR", f"{curve} avec G = {generator}")

    _, alice_public = keypair(curve, generator, private=cfg.dA)
    _, bob_public = keypair(curve, generator, private=cfg.dB)
    step(
        "ÉTAPE 3/4 · CLÉS PRIVÉES ET PUBLIQUES",
        f"Q_A = {cfg.dA}G = {alice_public}\nQ_B = {cfg.dB}G = {bob_public}",
    )

    alice_shared = shared_secret(curve, private=cfg.dA, peer_public=bob_public)
    bob_shared = shared_secret(curve, private=cfg.dB, peer_public=alice_public)
    assert alice_shared == bob_shared
    step("ÉTAPE 5 · ECDH -> POINT PARTAGÉ", f"K = {alice_shared}")

    key = ec_to_cbc_key(alice_shared)
    iv = urandom(cfg.block_size)
    step("ÉTAPE 6 · CLÉ CBC ET IV", f"K_x = {key}")

    plain = pad(payload, cfg.block_size)
    blocks = split_blocks(plain, cfg.block_size)
    blocks_text = "\n".join(
        f"P_{i} = {to_bin(block)}" for i, block in enumerate(blocks, start=1)
    )
    step(
        "ÉTAPE 7 · PAYLOAD EN BLOCS BINAIRES",
        f"{len(blocks)} bloc(s) de {cfg.block_size} octets après padding PKCS#7",
    )

    cipher = cbc_encrypt(blocks, key, iv)
    xors_text = "\n".join(
        f"P_{i} XOR {'IV' if i == 1 else f'C_{i - 1}'} = {to_bin(xor_bytes(block, iv if i == 1 else cipher[i - 2]))}"
        for i, block in enumerate(blocks, start=1)
    )
    ciphers_text = "\n".join(
        f"C_{i} = E_{key}(...) = {to_bin(block)}"
        for i, block in enumerate(cipher, start=1)
    )
    step(
        "ÉTAPE 8 · MODE CBC",
        f"{len(cipher)} bloc(s) chiffré(s) : C_i = E_K(P_i XOR C_{{i-1}})",
    )

    ciphertext = b"".join(cipher)
    files = [
        ("IV binaire", save_binary("iv", to_bin(iv))),
        ("Payload binaire", save_binary("payload", to_bin(payload))),
        ("Blocs P_i (padding)", save_binary("blocks", blocks_text)),
        ("P_i XOR (CBC)", save_binary("xor", xors_text)),
        ("Blocs chiffrés C_i", save_binary("cipher_blocks", ciphers_text)),
        ("Texte chiffré C", save_binary("ciphertext", to_bin(ciphertext))),
    ]
    step(
        "FICHIERS ÉCRITS DANS output/",
        "\n".join(f"{label}: {path}" for label, path in files),
    )

    recovered = unpad(b"".join(cbc_decrypt(cipher, key, iv)))
    if payload_type == "number":
        body = f"Déchiffré : {bytes_to_number(recovered)} (doit être {cfg.number})"
    else:
        body = f"Déchiffré : {recovered!r} (doit être {cfg.message!r})"
    step("DÉCHIFFREMENT (VÉRIFICATION)", body)


if __name__ == "__main__":
    try:
        main()
    except EOFError:
        print("Saisie interrompue.")
    except (ValueError, FileNotFoundError) as exc:
        print(f"Erreur : {exc}")
