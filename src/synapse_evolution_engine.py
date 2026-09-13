import numpy as np
from typing import List, Tuple, Dict
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Genome:
    """Represents the neural weights for a single agent."""
    def __init__(self, input_size: int = 8, hidden_size: int = 16, output_size: int = 4):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Weights
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2. / input_size)
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2. / hidden_size)
        
        # Biases
        self.b1 = np.zeros(hidden_size)
        self.b2 = np.zeros(output_size)
        
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Feedforward network with tanh activation for hidden layer."""
        z1 = np.dot(x, self.W1) + self.b1
        a1 = np.tanh(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        return np.tanh(z2) # outputs in [-1, 1]

def mutate(genome: Genome, mutation_rate: float = 0.1, sigma: float = 0.5) -> None:
    """Applies Gaussian noise perturbation to genome weights and biases."""
    for param in [genome.W1, genome.W2, genome.b1, genome.b2]:
        mask = np.random.rand(*param.shape) < mutation_rate
        noise = np.random.randn(*param.shape) * sigma
        param[mask] += noise[mask]

def crossover(parent1: Genome, parent2: Genome) -> Tuple[Genome, Genome]:
    """Performs uniform crossover between two genomes."""
    child1, child2 = Genome(), Genome()
    
    for attr in ['W1', 'W2', 'b1', 'b2']:
        p1_val = getattr(parent1, attr)
        p2_val = getattr(parent2, attr)
        
        mask = np.random.rand(*p1_val.shape) > 0.5
        
        c1_val = np.where(mask, p1_val, p2_val)
        c2_val = np.where(mask, p2_val, p1_val)
        
        setattr(child1, attr, c1_val)
        setattr(child2, attr, c2_val)
        
    return child1, child2

def evaluate_fitness(genome: Genome) -> float:
    """
    Evaluates fitness based on Pareto-optimal criteria proxy.
    Simulates environment response to outputs.
    """
    # Simulate a fast episode
    lifespan = 0
    energy = 100.0
    food_gathered = 0
    
    # 100 simulation steps
    for _ in range(100):
        # 8 sensor inputs: Raycast distances(4), energy(1), food_vec(2), velocity(1)
        inputs = np.random.rand(8)
        inputs[4] = energy / 100.0 # Normalize energy
        
        outputs = genome.forward(inputs)
        
        # Thrust, Angular Vel, Repro, Shield
        thrust = (outputs[0] + 1) / 2 # 0 to 1
        shield = outputs[3] > 0
        
        energy -= (thrust * 0.5 + (0.2 if shield else 0.0) + 0.1) # Cost of action
        if energy <= 0:
            break
            
        # Random chance to find food based on movement
        if np.random.rand() < 0.1 * thrust:
            food_gathered += 1
            energy = min(100.0, energy + 20)
            
        lifespan += 1
        
    # Aggregate fitness score: Lifespan + Food * 10
    return lifespan + food_gathered * 10.0

def run_simulation(population_size: int = 100, generations: int = 1000):
    """Runs the high-speed evolutionary harness."""
    population = [Genome() for _ in range(population_size)]
    
    start_time = time.time()
    best_fitness_history = []
    
    for gen in range(generations):
        # Evaluate
        fitness_scores = [evaluate_fitness(g) for g in population]
        best_idx = np.argmax(fitness_scores)
        best_fitness = fitness_scores[best_idx]
        best_fitness_history.append(best_fitness)
        
        if (gen + 1) % 100 == 0:
            logging.info(f"Generation {gen+1:4d} | Best Fitness: {best_fitness:7.2f} | Avg Fitness: {np.mean(fitness_scores):7.2f}")
            
        # Select top 20%
        sorted_indices = np.argsort(fitness_scores)[::-1]
        top_20 = sorted_indices[:population_size // 5]
        
        new_population = [population[i] for i in top_20]
        
        # Breed new population
        while len(new_population) < population_size:
            p1_idx = np.random.choice(top_20)
            p2_idx = np.random.choice(top_20)
            c1, c2 = crossover(population[p1_idx], population[p2_idx])
            mutate(c1)
            mutate(c2)
            new_population.extend([c1, c2])
            
        population = new_population[:population_size]
        
    duration = time.time() - start_time
    logging.info(f"Simulation completed in {duration:.2f} seconds.")
    return best_fitness_history

if __name__ == "__main__":
    logging.info("Initializing Synapse Evolution Engine...")
    run_simulation(population_size=100, generations=1000)
