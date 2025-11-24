"""GeneticAlgorithm main orchestrator for the genetic algorithm."""

import random
import numpy as np
from typing import List, Tuple, Optional, Dict
from multiprocessing import Pool
from tqdm import tqdm
from src.models.chromosome import Chromosome
from src.models.problem_data import ProblemData
from src.core.route_initializer import RouteInitializer
from src.core.fitness_evaluator import FitnessEvaluator
from src.core.evolution_operator import EvolutionOperator
from src.config import (
    NUM_CHROMOSOMES, MAX_ITERATIONS, INITIAL_MUTATION_RATE,
    SELECTION_RATIO, CONVERGENCE_THRESHOLD, CONVERGENCE_WINDOW, ELITISM_SIZE,
    NUM_WORKERS
)
from src.timing import reset_timing_stats, print_timing_summary


_POOL_EVALUATOR: Optional[FitnessEvaluator] = None


def _init_pool(problem_data: ProblemData) -> None:
    """Initializer to share evaluator across worker processes."""
    global _POOL_EVALUATOR
    _POOL_EVALUATOR = FitnessEvaluator(problem_data)


def _evaluate_single(chromosome: Chromosome) -> Tuple[float, Dict]:
    """Evaluate a chromosome inside a worker process."""
    if _POOL_EVALUATOR is None:
        raise RuntimeError("Pool evaluator not initialized")
    fitness, stats = _POOL_EVALUATOR.evaluate(chromosome)
    return fitness, stats


class GeneticAlgorithm:
    """Main genetic algorithm orchestrator."""

    def __init__(self, problem_data: ProblemData):
        """
        Initialize genetic algorithm.

        Args:
            problem_data: ProblemData containing problem information.
        """
        self.problem_data = problem_data
        self.initializer = RouteInitializer(problem_data)
        self.evaluator = FitnessEvaluator(problem_data)
        self.evolution = EvolutionOperator(problem_data)
        self.population: List[Chromosome] = []
        self.best_chromosome: Optional[Chromosome] = None
        self.best_stats: Optional[Dict] = None

    def run(self, verbose: bool = True) -> Tuple[Chromosome, Dict]:
        """
        Run the genetic algorithm.

        Args:
            verbose: Whether to print progress.

        Returns:
            Tuple of (best_chromosome, statistics_dict).
        """
        # Reset timing statistics
        reset_timing_stats()

        # Initialize population
        self._initialize_population()

        # Evaluate initial population
        self._evaluate_population(verbose=verbose)

        # Track best solution
        self._update_best_solution()

        # Track convergence
        fitness_history = []
        best_fitness = self.best_chromosome.get_fitness()

        if best_fitness is not None:
            fitness_history.append(best_fitness)

        # Evolution loop
        for generation in range(MAX_ITERATIONS):
            # Calculate annealed mutation rate
            mutation_rate = EvolutionOperator.calculate_annealed_rate(
                INITIAL_MUTATION_RATE, generation, MAX_ITERATIONS
            )

            # Evolve one generation
            self._evolve_generation(mutation_rate, generation, verbose)

            # Update best solution
            self._update_best_solution()

            # Track fitness
            if self.best_chromosome and self.best_chromosome.get_fitness() is not None:
                current_fitness = self.best_chromosome.get_fitness()
                fitness_history.append(current_fitness)

                # Check convergence
                if self._check_convergence(fitness_history):
                    if verbose:
                        print(f"Converged at generation {generation}")
                    break

                # Print progress
                if verbose and (generation % 50 == 0 or generation < 100):
                    avg_fitness = np.mean([c.get_fitness() or float('inf') for c in self.population])
                    std_fitness = np.std([c.get_fitness() or float('inf') for c in self.population])
                    print(f"Generation {generation}: Best={current_fitness:.2f}, "
                          f"Avg={avg_fitness:.2f}, Std={std_fitness:.2f}, Mutation={mutation_rate:.4f}"
                          f" Unserved Passengers={self.best_stats['unserved_passengers'] if self.best_stats else 'N/A'}"
                          f" Total Stops={self.best_stats['total_stops'] if self.best_stats else 'N/A'}")

        # Print final results
        if verbose:
            if self.best_chromosome and self.best_chromosome.get_fitness() is not None:
                print(f"\nFinal best fitness: {self.best_chromosome.get_fitness():.2f}")
            if self.best_stats:
                print(f"Unserved passengers: {self.best_stats['unserved_passengers']}")
                print(f"Total stops: {self.best_stats['total_stops']}")
                print(f"Total flights: {self.best_stats['total_flights']}")

        # Print timing summary
        print_timing_summary()

        return self.best_chromosome, self.best_stats

    def _initialize_population(self) -> None:
        """Initialize the population with random chromosomes."""
        self.population = []
        for _ in range(NUM_CHROMOSOMES):
            chromosome = self.initializer.initialize_chromosome()
            self.population.append(chromosome)

    def _evaluate_population(self, verbose: bool = False) -> None:
        """Evaluate fitness for all chromosomes in population."""
        self._evaluate_chromosomes(self.population, verbose, "Evaluating init population")

    def _select_parents(self) -> List[Chromosome]:
        """
        Select parents for reproduction.

        Returns:
            List of selected parent chromosomes.
        """
        # Sort by fitness (lower is better)
        sorted_pop = sorted(
            self.population,
            key=lambda c: c.get_fitness() if c.get_fitness() is not None else float('inf')
        )

        # Select best individuals
        num_select = int(NUM_CHROMOSOMES * SELECTION_RATIO)
        return sorted_pop[:num_select]

    def _evolve_generation(self, mutation_rate: float, generation_idx: int, verbose: bool) -> None:
        """
        Evolve one generation.

        Args:
            mutation_rate: Current mutation rate.
            generation_idx: Current generation number (for progress display).
            verbose: Whether to show per-generation progress bars.
        """
        # Select parents
        parents = self._select_parents()

        # Create offspring
        offspring = []
        for i in range(0, len(parents) - 1, 2):
            parent1 = parents[i]
            parent2 = parents[i + 1] if i + 1 < len(parents) else parents[0]

            # Crossover with probability
            if random.random() < 0.7:
                child1, child2 = self.evolution.crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # Mutate offspring
            if random.random() < mutation_rate:
                child1 = self.evolution.mutate(child1, mutation_rate)
            if random.random() < mutation_rate:
                child2 = self.evolution.mutate(child2, mutation_rate)

            offspring.append(child1)
            if len(offspring) < NUM_CHROMOSOMES:
                offspring.append(child2)

        # Ensure we have enough offspring
        while len(offspring) < NUM_CHROMOSOMES:
            parent = random.choice(parents)
            offspring.append(parent.copy())

        # Evaluate offspring
        self._evaluate_chromosomes(
            offspring,
            verbose,
            f"Generation {generation_idx} evaluation"
        )

        # Elitism: keep best individuals
        sorted_pop = sorted(
            self.population,
            key=lambda c: c.get_fitness() if c.get_fitness() is not None else float('inf')
        )

        # Replace worst offspring with best from previous generation
        for i in range(min(ELITISM_SIZE, len(sorted_pop))):
            worst_idx = max(
                range(len(offspring)),
                key=lambda j: offspring[j].get_fitness() if offspring[j].get_fitness() is not None else float('inf')
            )
            best_ind = sorted_pop[i]
            offspring[worst_idx] = best_ind.copy()
            offspring[worst_idx].set_fitness(best_ind.get_fitness())

        # Update population
        self.population = offspring

    def _evaluate_chromosomes(self, chromosomes: List[Chromosome], verbose: bool, desc: str) -> None:
        """
        Evaluate a list of chromosomes, optionally in parallel.

        Args:
            chromosomes: List of chromosomes to evaluate.
            verbose: Whether to show progress bars.
            desc: tqdm description.
        """
        if not chromosomes:
            return

        if NUM_WORKERS and NUM_WORKERS > 1:
            with Pool(
                processes=NUM_WORKERS,
                initializer=_init_pool,
                initargs=(self.problem_data,)
            ) as pool:
                results_iter = pool.imap(_evaluate_single, chromosomes)
                results = list(
                    tqdm(
                        results_iter,
                        total=len(chromosomes),
                        desc=desc,
                        leave=False,
                        disable=not verbose
                    )
                )
        else:
            results = []
            for chrom in tqdm(
                chromosomes,
                desc=desc,
                leave=False,
                disable=not verbose
            ):
                results.append(self.evaluator.evaluate(chrom))

        for chrom, (fitness, stats) in zip(chromosomes, results):
            chrom.set_fitness(fitness)

    def _update_best_solution(self) -> None:
        """Update the best solution found so far."""
        best = min(
            self.population,
            key=lambda c: c.get_fitness() if c.get_fitness() is not None else float('inf')
        )

        if best.get_fitness() is not None:
            if (self.best_chromosome is None or
                self.best_chromosome.get_fitness() is None or
                best.get_fitness() < self.best_chromosome.get_fitness()):

                self.best_chromosome = best.copy()
                _, self.best_stats = self.evaluator.evaluate(self.best_chromosome)

    def _check_convergence(self, fitness_history: List[float]) -> bool:
        """
        Check if algorithm has converged.

        Args:
            fitness_history: List of fitness values over generations.

        Returns:
            True if converged, False otherwise.
        """
        if len(fitness_history) < CONVERGENCE_WINDOW:
            return False

        recent_improvement = (
            fitness_history[-CONVERGENCE_WINDOW] - fitness_history[-1]
        )
        return recent_improvement < CONVERGENCE_THRESHOLD

    def get_best_solution(self) -> Tuple[Optional[Chromosome], Optional[Dict]]:
        """
        Get the best solution found.

        Returns:
            Tuple of (best_chromosome, statistics_dict).
        """
        return self.best_chromosome, self.best_stats
