"""
secp256k1.py — Minimal pure-Python secp256k1 ECDSA (sign/verify).
No external dependencies. For identity-signing use in the MATN chain,
not audited for production custody use.
"""

import hashlib
import os

# secp256k1 curve parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (Gx, Gy)


def inverse_mod(k, p):
    return pow(k, p - 2, p)


def ec_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        m = (3 * x1 * x1 + A) * inverse_mod(2 * y1, P) % P
    else:
        m = (y2 - y1) * inverse_mod(x2 - x1, P) % P
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)


def ec_mul(k, point):
    result = None
    addend = point
    while k:
        if k & 1:
            result = ec_add(result, addend)
        addend = ec_add(addend, addend)
        k >>= 1
    return result


def generate_private_key() -> int:
    return int.from_bytes(os.urandom(32), "big") % N


def private_to_public(privkey: int):
    return ec_mul(privkey, G)


def sha256_int(data: bytes) -> int:
    return int.from_bytes(hashlib.sha256(data).digest(), "big")


def sign(privkey: int, message: bytes, k: int = None) -> tuple:
    z = sha256_int(message)
    if k is None:
        # Deterministic-ish nonce derived from privkey+message (RFC6979-lite,
        # not a full compliant implementation but avoids nonce reuse across msgs)
        k = sha256_int(privkey.to_bytes(32, "big") + message) % N
        if k == 0:
            k = 1
    x, _ = ec_mul(k, G)
    r = x % N
    if r == 0:
        return sign(privkey, message, k=k + 1)
    k_inv = inverse_mod(k, N)
    s = (k_inv * (z + r * privkey)) % N
    if s == 0:
        return sign(privkey, message, k=k + 1)
    # Canonical low-s
    if s > N // 2:
        s = N - s
    return (r, s)


def verify(pubkey: tuple, message: bytes, signature: tuple) -> bool:
    r, s = signature
    if not (1 <= r < N and 1 <= s < N):
        return False
    z = sha256_int(message)
    w = inverse_mod(s, N)
    u1 = (z * w) % N
    u2 = (r * w) % N
    point = ec_add(ec_mul(u1, G), ec_mul(u2, pubkey))
    if point is None:
        return False
    return (point[0] % N) == r


def pubkey_to_hex(pubkey: tuple, compressed: bool = True) -> str:
    x, y = pubkey
    if compressed:
        prefix = b"\x02" if y % 2 == 0 else b"\x03"
        return (prefix + x.to_bytes(32, "big")).hex()
    return (b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")).hex()


def sig_to_hex(sig: tuple) -> str:
    r, s = sig
    return r.to_bytes(32, "big").hex() + s.to_bytes(32, "big").hex()


def hex_to_sig(h: str) -> tuple:
    r = int(h[:64], 16)
    s = int(h[64:], 16)
    return (r, s)
