from ecc import ECCurve, ECPoint


def keypair(curve: ECCurve, generator: ECPoint, private: int) -> tuple[int, ECPoint]:
    """Génère (clé privée, clé publique = private · G)."""
    public = curve.mul(private, generator)
    if public is None:
        raise ValueError("clé privée invalide : private · G = O")
    return private, public


def shared_secret(curve: ECCurve, private: int, peer_public: ECPoint) -> ECPoint:
    """Clé partagée K = private · peer_public (le point de rencontre de l'ECDH)."""
    secret = curve.mul(private, peer_public)
    if secret is None:
        raise ValueError("la clé partagée est le point à l'infini")
    return secret
