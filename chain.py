"""
MATN Chain Implementation
Complete shortest-path blockchain with identity binding and magnetometer constraints.
Quantum superposition pathfinding framework.
"""

import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from block import MATNBlock, MATNBlockValidator
from merkle import MerkleTree, MerkleNode
from secp256k1 import generate_private_key, private_to_public, pubkey_to_hex


class MATPNChain:
    """MATN (Magnetometer-Authenticated Topological Path Network) blockchain."""
    
    def __init__(self, identity_pubkey: str, privkey: int):
        """
        Initialize MATN chain.
        
        Args:
            identity_pubkey: Creator's public key (identity-bound chain)
            privkey: Creator's private key (for signing blocks)
        """
        self.identity_pubkey = identity_pubkey
        self.privkey = privkey
        self.blocks: List[MATNBlock] = []
        self.merkle_tree = MerkleTree()
        self.quantum_states: List[Dict] = []  # Superposition path states
        self.validator = MANBlockValidator()
        self.created_at = datetime.now().isoformat()
    
    def add_block(
        self,
        path_data: Dict,
        field_vector: Dict,
    ) -> MATNBlock:
        """
        Add block to chain.
        
        Args:
            path_data: Shortest-path segment
            field_vector: Magnetometer field measurements
        
        Returns:
            New block
        """
        previous_hash = self.blocks[-1].hash if self.blocks else "0"
        index = len(self.blocks)
        
        block = MATNBlock(
            index=index,
            previous_hash=previous_hash,
            path_data=path_data,
            field_vector=field_vector,
            identity_pubkey=self.identity_pubkey,
            privkey=self.privkey,
        )
        
        # Validate block
        prev_block = self.blocks[-1] if self.blocks else None
        is_valid, reason = self.validator.validate_block(block, prev_block)
        
        if not is_valid:
            raise ValueError(f"Block validation failed: {reason}")
        
        self.blocks.append(block)
        
        # Add to Merkle tree for verification
        self.merkle_tree.add_path_segment(
            block.hash.encode(),
            field_vector.get("strength", 0.5),
        )
        
        return block
    
    def finalize_merkle_tree(self) -> str:
        """Build Merkle tree and return root hash."""
        return self.merkle_tree.build_tree()
    
    def add_quantum_superposition(
        self,
        path_alternatives: List[Dict],
    ) -> None:
        """
        Add quantum superposition state.
        Represents multiple possible shortest paths simultaneously.
        
        Args:
            path_alternatives: List of possible path states
        """
        state = {
            "timestamp": datetime.now().isoformat(),
            "superposition": path_alternatives,
            "amplitude_sum": sum(p.get("amplitude", 1.0) for p in path_alternatives),
        }
        self.quantum_states.append(state)
    
    def collapse_superposition(self, measurement: Dict) -> Dict:
        """
        Collapse quantum superposition to single path.
        Measurement simulates magnetometer observation.
        
        Args:
            measurement: Field measurement that collapses superposition
        
        Returns:
            Selected path
        """
        if not self.quantum_states:
            return {}
        
        latest_state = self.quantum_states[-1]
        alternatives = latest_state["superposition"]
        
        # Select path with highest field alignment to measurement
        best_path = max(
            alternatives,
            key=lambda p: self._field_alignment(p.get("field_vector", {}), measurement),
        )
        
        return best_path
    
    def _field_alignment(self, path_field: Dict, measurement: Dict) -> float:
        """Calculate field alignment between path and measurement."""
        dot_product = sum(
            path_field.get(axis, 0) * measurement.get(axis, 0)
            for axis in ["x", "y", "z"]
        )
        return dot_product
    
    def get_chain_stats(self) -> Dict:
        """Get chain statistics."""
        total_energy = sum(b.energy_cost() for b in self.blocks)
        avg_field = sum(
            b.field_vector.get("strength", 0) for b in self.blocks
        ) / len(self.blocks) if self.blocks else 0
        
        return {
            "chain_length": len(self.blocks),
            "total_energy_cost": total_energy,
            "average_field_strength": avg_field,
            "quantum_states": len(self.quantum_states),
            "created_at": self.created_at,
            "identity_pubkey": self.identity_pubkey,
        }
    
    def to_json(self) -> str:
        """Export chain to JSON."""
        chain_data = {
            "metadata": self.get_chain_stats(),
            "blocks": [b.to_dict() for b in self.blocks],
            "merkle_root": (
                self.merkle_tree.root.hash if self.merkle_tree.root else None
            ),
            "quantum_states": self.quantum_states,
        }
        return json.dumps(chain_data, indent=2)
    
    def verify_chain_integrity(self) -> Tuple[bool, str]:
        """Verify entire chain integrity."""
        if not self.blocks:
            return True, "Empty chain"
        
        # Verify each block
        for i, block in enumerate(self.blocks):
            prev_block = self.blocks[i - 1] if i > 0 else None
            is_valid, reason = self.validator.validate_block(block, prev_block)
            
            if not is_valid:
                return False, f"Block {i} invalid: {reason}"
        
        # Verify Merkle tree
        if self.merkle_tree.root:
            all_verified = all(
                self.merkle_tree.verify_leaf(leaf)
                for leaf in self.merkle_tree.leaves
            )
            if not all_verified:
                return False, "Merkle tree verification failed"
        
        return True, "Chain integrity verified"


if __name__ == "__main__":
    # Example: Create and populate MATN chain
    privkey = generate_private_key()
    pubkey = private_to_public(privkey)
    pubkey_hex = pubkey_to_hex(pubkey, compressed=True)
    
    chain = MATPNChain(pubkey_hex, privkey)
    
    print("🔥 MATN Chain Initialization")
    print(f"Identity: {pubkey_hex}")
    print()
    
    # Add blocks with field constraints
    blocks_data = [
        {
            "path": {"segment": "origin", "coordinates": [0, 0, 0]},
            "field": {"x": 1.0, "y": 0.5, "z": 0.3, "strength": 0.85},
        },
        {
            "path": {"segment": "step_1", "coordinates": [1, 1, 0]},
            "field": {"x": 1.2, "y": 0.7, "z": 0.4, "strength": 0.92},
        },
        {
            "path": {"segment": "step_2", "coordinates": [2, 2, 1]},
            "field": {"x": 1.1, "y": 0.8, "z": 0.5, "strength": 0.88},
        },
    ]
    
    for data in blocks_data:
        block = chain.add_block(data["path"], data["field"])
        print(f"✅ Block {block.index}: {block.hash[:16]}...")
    
    print()
    
    # Add quantum superposition
    alternatives = [
        {"segment": "quantum_1", "amplitude": 0.6, "field_vector": {"x": 1.0, "y": 0.5, "z": 0.3}},
        {"segment": "quantum_2", "amplitude": 0.4, "field_vector": {"x": 1.1, "y": 0.6, "z": 0.4}},
    ]
    chain.add_quantum_superposition(alternatives)
    print(f"🌊 Quantum superposition added ({len(alternatives)} alternatives)")
    
    # Finalize Merkle tree
    merkle_root = chain.finalize_merkle_tree()
    print(f"🌳 Merkle root: {merkle_root[:16]}...")
    print()
    
    # Verify chain
    is_valid, reason = chain.verify_chain_integrity()
    print(f"✅ Chain integrity: {is_valid} ({reason})")
    print()
    
    # Stats
    stats = chain.get_chain_stats()
    print("📊 Chain Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
