"""
MATN Identity Sync PoC
Syncing identity (Martin Kipkurui Tanui, 1985-07-16) with MATN chain.
Generated hashes from identity + secp256k1 framework.
"""

import hashlib
from secp256k1 import (
    generate_private_key,
    private_to_public,
    sign,
    verify,
    pubkey_to_hex,
    sig_to_hex,
)

# Identity data
NAME = "Martin Kipkurui Tanui"
BIRTHDATE = "1985-07-16"
IDENTITY_STRING = f"{NAME}:{BIRTHDATE}"

# Generate hashes from identity
def identity_to_hashes(identity: str):
    """Convert identity to cryptographic hashes."""
    identity_bytes = identity.encode("utf-8")
    
    sha256_hash = hashlib.sha256(identity_bytes).hexdigest()
    sha512_hash = hashlib.sha512(identity_bytes).hexdigest()
    blake2b_hash = hashlib.blake2b(identity_bytes).hexdigest()
    
    return {
        "sha256": sha256_hash,
        "sha512": sha512_hash,
        "blake2b": blake2b_hash,
    }

# Generate MATN identity key from hash
def identity_to_privkey(identity: str) -> int:
    """Derive private key from identity hash."""
    identity_hash = hashlib.sha256(identity.encode("utf-8")).digest()
    privkey = int.from_bytes(identity_hash, "big")
    return privkey

# MATN sync operation
def matn_identity_sync(name: str, birthdate: str):
    """Execute MATN identity sync."""
    identity = f"{name}:{birthdate}"
    
    print(f"🔥 MATN Identity Sync PoC")
    print(f"Identity: {identity}")
    print()
    
    # Step 1: Identity hashes
    hashes = identity_to_hashes(identity)
    print("📊 Identity Hashes:")
    for hash_type, hash_value in hashes.items():
        print(f"  {hash_type}: {hash_value}")
    print()
    
    # Step 2: Derive private key from identity
    privkey = identity_to_privkey(identity)
    print(f"🔑 Private Key (from identity): {hex(privkey)}")
    print()
    
    # Step 3: Generate public key
    pubkey = private_to_public(privkey)
    pubkey_hex = pubkey_to_hex(pubkey, compressed=True)
    print(f"🔓 Public Key (compressed): {pubkey_hex}")
    print()
    
    # Step 4: Sign identity commitment
    message = identity.encode("utf-8")
    signature = sign(privkey, message)
    sig_hex = sig_to_hex(signature)
    print(f"✍️  Signature (identity commitment): {sig_hex}")
    print()
    
    # Step 5: Verify signature
    is_valid = verify(pubkey, message, signature)
    print(f"✅ Signature Valid: {is_valid}")
    print()
    
    # MATN Chain Entry
    matn_entry = {
        "identity": identity,
        "sha256": hashes["sha256"],
        "pubkey": pubkey_hex,
        "signature": sig_hex,
        "verified": is_valid,
    }
    
    print("⛓️  MATN Chain Entry:")
    import json
    print(json.dumps(matn_entry, indent=2))
    
    return matn_entry

if __name__ == "__main__":
    entry = matn_identity_sync(NAME, BIRTHDATE)
