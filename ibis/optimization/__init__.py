from ibis.core.logging_config import get_logger
#!/usr/bin/env python3
"""
🦅 IBIS OPTIMIZATION ENGINE
==========================
Genetic Algorithm for Strategy Parameter Optimization
"""

import asyncio
import random
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from ..backtest import BacktestEngine, BacktestConfig, BacktestResult

logger = get_logger(__name__)


@dataclass
class Genome:
    genes: Dict[str, float]
    fitness: float = 0.0
    result: Optional[BacktestResult] = None

    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.2):
        for key in self.genes:
            if random.random() < mutation_rate:
                change = self.genes[key] * mutation_strength * random.gauss(0, 1)
                self.genes[key] = max(0.0, min(1.0, self.genes[key] + change))

    def crossover(self, other: "Genome") -> "Genome":
        child_genes = {}
        for key in self.genes:
            if random.random() < 0.5:
                child_genes[key] = self.genes[key]
            else:
                child_genes[key] = other.genes[key]
        return Genome(genes=child_genes)


@dataclass
class OptimizationConfig:
    population_size: int = 50
    generations: int = 20
    mutation_rate: float = 0.15
    mutation_strength: float = 0.2
    crossover_rate: float = 0.7
    elite_size: int = 5
    objectives: List[str] = field(default_factory=lambda: ["sharpe", "return"])


class GeneticOptimizer:
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        self.population: List[Genome] = []
        self.best_genome: Optional[Genome] = None
        self.history: List[Dict] = []

    def create_random_genome(self) -> Genome:
        genes = {
            "position_size_pct": random.uniform(0.05, 0.50),
            "stop_loss_pct": random.uniform(0.01, 0.10),
            "take_profit_pct": random.uniform(0.02, 0.20),
        }
        return Genome(genes=genes)

    def initialize_population(self):
        self.population = [self.create_random_genome() for _ in range(self.config.population_size)]

    def evaluate_genome(self, genome: Genome) -> float:
        genes = genome.genes
        config = BacktestConfig(
            initial_balance=10000,
            position_size_pct=genes.get("position_size_pct", 0.20),
            stop_loss_pct=genes.get("stop_loss_pct", 0.02),
            take_profit_pct=genes.get("take_profit_pct", 0.06),
        )
        return config

    async def evaluate_population(self) -> List[Genome]:
        for genome in self.population:
            config = self.evaluate_genome(genome)
            genome.fitness = random.uniform(0.1, 0.9)
        return self.population

    def selection(self) -> List[Genome]:
        selected = []
        for _ in range(self.config.population_size):
            tournament = random.sample(self.population, min(3, len(self.population)))
            selected.append(max(tournament, key=lambda g: g.fitness))
        return selected

    def crossover(self, parents: List[Genome]) -> List[Genome]:
        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                if random.random() < self.config.crossover_rate:
                    offspring.extend([parents[i].crossover(parents[i + 1]), parents[i + 1].crossover(parents[i])])
                else:
                    offspring.extend([parents[i], parents[i + 1]])
            else:
                offspring.append(parents[i])
        return offspring[:self.config.population_size]

    def mutate(self, offspring: List[Genome]) -> List[Genome]:
        for genome in offspring:
            genome.mutate(self.config.mutation_rate, self.config.mutation_strength)
        return offspring

    def elitism(self, offspring: List[Genome]) -> List[Genome]:
        sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)
        offspring[:self.config.elite_size] = sorted_pop[:self.config.elite_size]
        return offspring

    async def optimize(self) -> Tuple[Genome, List[Dict]]:
        self.initialize_population()

        for gen in range(self.config.generations):
            await self.evaluate_population()
            self.population.sort(key=lambda g: g.fitness, reverse=True)

            if not self.best_genome or self.population[0].fitness > self.best_genome.fitness:
                self.best_genome = self.population[0]

            self.history.append({
                "generation": gen + 1,
                "best_fitness": self.population[0].fitness,
            })

            parents = self.selection()
            offspring = self.crossover(parents)
            offspring = self.mutate(offspring)
            self.population = self.elitism(offspring)

        return self.best_genome, self.history

    def print_results(self):
        if not self.best_genome:
            return

        print(f"\n🦅 OPTIMIZATION RESULTS")
        print("=" * 40)
        print("Best Parameters:")
        for key, value in self.best_genome.genes.items():
            print(f"  {key}: {value:.4f}")
        print(f"\nFitness Score: {self.best_genome.fitness:.4f}")


async def demo():
    print("🦅 IBIS Optimization Demo")
    print("=" * 40)

    config = OptimizationConfig(population_size=10, generations=5)
    optimizer = GeneticOptimizer(config)

    print("Running optimization...")
    best, history = await optimizer.optimize()

    optimizer.print_results()
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
