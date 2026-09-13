import unittest
import asyncio
import sys
import os

# Ensure src module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.arena_distributed_mesh import (
    Vector2D, NeuralGenome, OrganismState, 
    MigrationPayload, SpatialPartitioningProtocol
)


class TestArenaMesh(unittest.IsolatedAsyncioTestCase):

    async def test_genome_serialization(self):
        genome = NeuralGenome(layers=4, synaptic_weights=[0.12, -0.54, 0.88, 1.2], mutation_rate=0.01)
        state = OrganismState(
            id="alpha_01",
            position=Vector2D(500.0, 500.0),
            velocity=Vector2D(15.0, -5.0),
            energy=100.0,
            genome=genome
        )
        
        payload = MigrationPayload(state)
        serialized = payload.serialize()
        
        self.assertIsInstance(serialized, str)
        
        deserialized_payload = MigrationPayload.deserialize(serialized)
        
        # Validate mathematical data integrity after deserialization
        self.assertEqual(deserialized_payload.state.id, "alpha_01")
        self.assertEqual(deserialized_payload.state.position.x, 500.0)
        self.assertEqual(deserialized_payload.state.position.y, 500.0)
        self.assertEqual(deserialized_payload.state.velocity.x, 15.0)
        self.assertEqual(deserialized_payload.state.energy, 100.0)
        self.assertEqual(deserialized_payload.state.genome.layers, 4)
        self.assertEqual(deserialized_payload.state.genome.synaptic_weights, [0.12, -0.54, 0.88, 1.2])
        self.assertEqual(deserialized_payload.state.genome.mutation_rate, 0.01)

    async def test_cross_boundary_handoff(self):
        # Setup Primary Sector (1)
        sector1 = SpatialPartitioningProtocol(current_node_sector=1)
        
        # Capture async migrations to mock network transport
        migrated_payloads = []
        async def mock_migration_handler(payload: MigrationPayload, target_sector: int):
            migrated_payloads.append((payload, target_sector))
            
        sector1.on_migration_required = mock_migration_handler
        
        # Spawn an organism about to cross the X=1000 boundary
        genome = NeuralGenome(layers=3, synaptic_weights=[], mutation_rate=0.05)
        org = OrganismState(
            id="migrant_x1",
            position=Vector2D(995.0, 500.0),
            velocity=Vector2D(10.0, 0.0), # Will cross to 1005.0 on update
            energy=85.5,
            genome=genome
        )
        
        sector1.organisms[org.id] = org
        
        # Step simulation
        await sector1.update_organism(org)
        
        # Assert organism departed from Sector 1
        self.assertNotIn("migrant_x1", sector1.organisms)
        self.assertEqual(len(migrated_payloads), 1)
        
        payload, target = migrated_payloads[0]
        self.assertEqual(target, 2)
        self.assertEqual(payload.state.id, "migrant_x1")
        
        # Setup Edge Sector (2) and receive network payload
        sector2 = SpatialPartitioningProtocol(current_node_sector=2)
        await sector2.receive_migration(payload.serialize())
        
        # Assert arrival in Sector 2
        self.assertIn("migrant_x1", sector2.organisms)
        # State should reflect the physics integration from the previous step
        self.assertEqual(sector2.organisms["migrant_x1"].position.x, 1005.0)


if __name__ == "__main__":
    unittest.main()
