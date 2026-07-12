"""
MATN Vectorization Implementation
Convert knot equations to vector field constraints.
Field-based shortest path through solution space.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from knot_equation import KnotEquation, KnotCrossing


class VectorField:
    """Vector field representing knot solution space."""
    
    def __init__(self, dimension: int = 3, resolution: int = 100):
        """
        Initialize vector field.
        
        Args:
            dimension: Field dimension (3D for Bitcoin keys)
            resolution: Grid resolution for field computation
        """
        self.dimension = dimension
        self.resolution = resolution
        self.field_grid: Optional[np.ndarray] = None
        self.gradients: Optional[np.ndarray] = None
    
    def vectorize_knot(self, knot: KnotEquation) -> np.ndarray:
        """
        Vectorize knot into field constraints.
        
        Args:
            knot: KnotEquation instance
        
        Returns:
            Vector field representation
        """
        crossings = knot.crossings
        
        if not crossings:
            return np.zeros((self.resolution, self.dimension))
        
        # Stack all crossing vectors
        vectors = np.array([c.vector for c in crossings])
        
        # Compute field grid
        self.field_grid = np.zeros((self.resolution, self.dimension))
        
        for i in range(self.resolution):
            position = (i / self.resolution) * 2 * np.pi
            
            # Interpolate through crossings
            crossing_idx = int((i / self.resolution) * len(crossings))
            crossing_idx = min(crossing_idx, len(crossings) - 1)
            
            crossing = crossings[crossing_idx]
            
            # Field value = crossing vector rotated by position
            angle = position
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
            
            field_value = rotation_matrix @ crossing.vector
            self.field_grid[i] = field_value
        
        return self.field_grid
    
    def compute_gradient_field(self) -> np.ndarray:
        """Compute gradient of vector field (for optimization)."""
        if self.field_grid is None:
            return np.zeros((self.resolution, self.dimension))
        
        gradients = np.zeros_like(self.field_grid)
        
        for d in range(self.dimension):
            for i in range(1, self.resolution - 1):
                gradients[i, d] = (
                    self.field_grid[i + 1, d] - self.field_grid[i - 1, d]
                ) / 2.0
        
        self.gradients = gradients
        return gradients
    
    def find_critical_points(self, threshold: float = 0.01) -> List[int]:
        """
        Find critical points in field (potential solutions).
        
        Args:
            threshold: Gradient magnitude threshold
        
        Returns:
            Indices of critical points
        """
        if self.gradients is None:
            self.compute_gradient_field()
        
        critical_points = []
        
        for i in range(self.resolution):
            gradient_magnitude = np.linalg.norm(self.gradients[i])
            
            if gradient_magnitude < threshold:
                critical_points.append(i)
        
        return critical_points
    
    def field_energy(self, path: List[int]) -> float:
        """
        Calculate energy of a path through field.
        Lower energy = better solution (photosynthesis model).
        
        Args:
            path: List of indices along path
        
        Returns:
            Total energy cost
        """
        if self.field_grid is None:
            return float('inf')
        
        energy = 0.0
        
        for i in range(len(path) - 1):
            current_vec = self.field_grid[path[i]]
            next_vec = self.field_grid[path[i + 1]]
            
            # Energy = magnitude of field at each point
            energy += np.linalg.norm(current_vec)
            
            # Add transition cost
            transition = np.linalg.norm(next_vec - current_vec)
            energy += transition
        
        return energy
    
    def shortest_path_through_field(self) -> Tuple[List[int], float]:
        """
        Find shortest energy path through field.
        Uses gradient descent with field constraints.
        
        Returns:
            (path indices, total energy)
        """
        if self.field_grid is None:
            return [], float('inf')
        
        # Start from beginning
        path = [0]
        current_energy = 0.0
        
        # Greedy gradient descent
        for step in range(self.resolution - 1):
            current_idx = path[-1]
            current_vec = self.field_grid[current_idx]
            
            # Find neighbor with lowest energy
            best_next = current_idx
            best_energy = np.linalg.norm(current_vec)
            
            # Check nearby points
            for neighbor in range(max(0, current_idx - 5), min(self.resolution, current_idx + 6)):
                if neighbor not in path or neighbor == current_idx:
                    neighbor_vec = self.field_grid[neighbor]
                    neighbor_energy = np.linalg.norm(neighbor_vec)
                    
                    if neighbor_energy < best_energy:
                        best_energy = neighbor_energy
                        best_next = neighbor
            
            path.append(best_next)
            current_energy += best_energy
        
        return path, current_energy
    
    def vectorize_constraint(self, constraint_type: str, constraint_data: Dict) -> np.ndarray:
        """
        Vectorize a specific constraint.
        
        Args:
            constraint_type: Type of constraint ("field_strength", "bit_parity", etc.)
            constraint_data: Constraint parameters
        
        Returns:
            Constraint vector
        """
        constraint_vector = np.zeros(self.dimension)
        
        if constraint_type == "field_strength":
            strength = constraint_data.get("strength", 1.0)
            constraint_vector = np.array([strength, strength, strength])
        
        elif constraint_type == "bit_parity":
            bit_value = constraint_data.get("bit", 0)
            constraint_vector = np.array([bit_value, 1 - bit_value, 0.5])
        
        elif constraint_type == "energy_limit":
            limit = constraint_data.get("limit", 1.0)
            constraint_vector = np.array([limit, limit, limit])
        
        return constraint_vector
    
    def to_dict(self) -> Dict:
        """Export field to dictionary."""
        return {
            "dimension": self.dimension,
            "resolution": self.resolution,
            "field_shape": self.field_grid.shape if self.field_grid is not None else None,
            "has_gradients": self.gradients is not None,
        }


class FieldOptimizer:
    """Optimize solution through vector field."""
    
    @staticmethod
    def optimize_path(field: VectorField, iterations: int = 100) -> Tuple[List[int], float]:
        """
        Optimize path through field using gradient descent.
        
        Args:
            field: VectorField instance
            iterations: Number of optimization iterations
        
        Returns:
            (optimized path, final energy)
        """
        path, energy = field.shortest_path_through_field()
        
        for iteration in range(iterations):
            # Compute gradients
            gradients = field.compute_gradient_field()
            
            # Move along negative gradient
            new_path = [path[0]]
            for i in range(1, len(path) - 1):
                idx = path[i]
                gradient = gradients[idx]
                
                # Move in direction of negative gradient
                if np.linalg.norm(gradient) > 0.001:
                    direction = -gradient / np.linalg.norm(gradient)
                    step_size = 0.1
                    new_position = field.field_grid[idx] + step_size * direction
                    
                    # Find closest grid point
                    distances = np.linalg.norm(field.field_grid - new_position, axis=1)
                    closest_idx = np.argmin(distances)
                    new_path.append(closest_idx)
                else:
                    new_path.append(idx)
            
            new_path.append(path[-1])
            path = new_path
            energy = field.field_energy(path)
        
        return path, energy


if __name__ == "__main__":
    from knot_equation import KnotEquation
    
    # Example: Vectorize a knot and find shortest path
    test_key = "1" * 36 + "0" * 37
    knot = KnotEquation(bit_length=73)
    knot.encode_key_as_knot(test_key)
    
    print("🔀 Vectorizing knot...")
    field = VectorField(dimension=3, resolution=100)
    field_grid = field.vectorize_knot(knot)
    print(f"Field grid shape: {field_grid.shape}")
    print()
    
    # Find critical points
    critical_points = field.find_critical_points()
    print(f"🎯 Critical points found: {len(critical_points)}")
    print()
    
    # Find shortest path
    path, energy = field.shortest_path_through_field()
    print(f"📍 Shortest path: {len(path)} steps")
    print(f"⚡ Path energy: {energy:.6f}")
    print()
    
    # Optimize
    optimizer = FieldOptimizer()
    optimized_path, optimized_energy = optimizer.optimize_path(field, iterations=50)
    print(f"🔧 After optimization: {len(optimized_path)} steps")
    print(f"⚡ Optimized energy: {optimized_energy:.6f}")
