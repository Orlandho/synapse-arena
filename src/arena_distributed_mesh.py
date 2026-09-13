import asyncio
import json
from dataclasses import dataclass, asdict
from typing import Tuple, Dict, Any, Callable, Awaitable

@dataclass
class Vector2D:
    x: float
    y: float

@dataclass
class NeuralGenome:
    layers: int
    synaptic_weights: list[float]
    mutation_rate: float

@dataclass
class OrganismState:
    id: str
    position: Vector2D
    velocity: Vector2D
    energy: float
    genome: NeuralGenome

class MigrationPayload:
    """Encapsulates the data payload required to transfer an organism across nodes."""
    def __init__(self, state: OrganismState):
        self.state = state
    
    def serialize(self) -> str:
        """Serializes the organism state into a JSON string for network transmission."""
        return json.dumps(asdict(self.state))
    
    @classmethod
    def deserialize(cls, data: str) -> 'MigrationPayload':
        """Deserializes a JSON string back into an OrganismState and wraps it in a payload."""
        parsed = json.loads(data)
        parsed['position'] = Vector2D(**parsed['position'])
        parsed['velocity'] = Vector2D(**parsed['velocity'])
        parsed['genome'] = NeuralGenome(**parsed['genome'])
        return cls(OrganismState(**parsed))

class SpatialPartitioningProtocol:
    """Manages spatial bounds, organism positions, and inter-node migrations."""
    def __init__(self, current_node_sector: int):
        self.current_node_sector = current_node_sector
        self.organisms: Dict[str, OrganismState] = {}
        # Callback for handling cross-boundary events
        self.on_migration_required: Callable[[MigrationPayload, int], Awaitable[None]] = self.default_migration_handler
        
    def determine_sector(self, x: float) -> int:
        """Determines the computational node sector based on the X coordinate."""
        if 0 <= x < 1000:
            return 1 # Primary Grid (Desktop)
        elif 1000 <= x <= 2000:
            return 2 # Edge Grid (Laptop)
        else:
            raise ValueError(f"Position X={x} is out of bounds (0-2000).")

    async def default_migration_handler(self, payload: MigrationPayload, target_sector: int) -> None:
        """Default stub for migration network transport."""
        pass 
        
    async def update_organism(self, org: OrganismState) -> None:
        """
        Updates the organism's physical state using an Euler integration step,
        and manages spatial boundary checks for inter-node handoffs.
        """
        # Vector transformation step
        org.position.x += org.velocity.x
        org.position.y += org.velocity.y
        
        try:
            target_sector = self.determine_sector(org.position.x)
        except ValueError:
            # In a robust simulation, handle destruction, bouncing, or wrap-around
            return
            
        if target_sector != self.current_node_sector:
            # Organism crossed the boundary into a new node's partition
            payload = MigrationPayload(org)
            await self.on_migration_required(payload, target_sector)
            # Remove from local processing after successful handoff attempt
            if org.id in self.organisms:
                del self.organisms[org.id]
        else:
            # Ensure local tracking
            self.organisms[org.id] = org
            
    async def receive_migration(self, payload_data: str) -> None:
        """Processes an incoming migration payload from the network."""
        payload = MigrationPayload.deserialize(payload_data)
        self.organisms[payload.state.id] = payload.state
