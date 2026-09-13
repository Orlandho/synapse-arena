import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from synapse_evolution_engine import Genome, mutate, crossover, evaluate_fitness


class TestSynapseEvolution(unittest.TestCase):

    def test_genome_initialization(self):
        g = Genome()
        self.assertEqual(g.W1.shape, (8, 16))
        self.assertEqual(g.W2.shape, (16, 4))
        self.assertEqual(g.b1.shape, (16,))
        self.assertEqual(g.b2.shape, (4,))

    def test_feedforward_bounds(self):
        g = Genome()
        x = np.random.rand(8)
        out = g.forward(x)
        self.assertEqual(out.shape, (4,))
        self.assertTrue(np.all(out >= -1.0) and np.all(out <= 1.0))

    def test_mutation(self):
        g = Genome()
        original_W1 = np.copy(g.W1)
        mutate(g, mutation_rate=1.0, sigma=0.5)
        self.assertFalse(np.array_equal(g.W1, original_W1))

    def test_crossover(self):
        g1, g2 = Genome(), Genome()
        c1, c2 = crossover(g1, g2)
        self.assertEqual(c1.W1.shape, g1.W1.shape)
        self.assertEqual(c1.W2.shape, g1.W2.shape)

    def test_fitness_evaluation(self):
        g = Genome()
        fitness = evaluate_fitness(g)
        self.assertIsInstance(fitness, float)
        self.assertGreaterEqual(fitness, 0)


if __name__ == "__main__":
    unittest.main()
