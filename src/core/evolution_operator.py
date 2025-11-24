"""EvolutionOperator handles crossover and mutation."""

import random
from typing import Tuple
from src.models.chromosome import Chromosome
from src.models.aircraft_route import AircraftRoute
from src.models.problem_data import ProblemData
from src.core.route_initializer import RouteInitializer
from src.core.route_scheduler import RouteScheduler
from src.config import START_TIME, END_TIME, COOLDOWN_TIME
from src.timing import timing_decorator


class EvolutionOperator:
    """Handles crossover and mutation operations."""

    def __init__(self, problem_data: ProblemData):
        """
        Initialize evolution operator.

        Args:
            problem_data: ProblemData containing problem information.
        """
        self.problem_data = problem_data
        self.initializer = RouteInitializer(problem_data)

    @timing_decorator
    def crossover(
        self,
        parent1: Chromosome,
        parent2: Chromosome,
        crossover_ratio: float = 0.5
    ) -> Tuple[Chromosome, Chromosome]:
        """
        Crossover two chromosomes by swapping a percentage of aircraft.

        Args:
            parent1: First parent chromosome.
            parent2: Second parent chromosome.
            crossover_ratio: Fraction of aircraft to swap (default 0.5).

        Returns:
            Tuple of (offspring1, offspring2).
        """
        num_aircraft = parent1.get_num_aircraft()
        num_to_swap = int(num_aircraft * crossover_ratio)

        # Get routes from parents
        routes1 = parent1.get_routes()
        routes2 = parent2.get_routes()

        # Randomly select aircraft indices to swap
        swap_indices = random.sample(range(num_aircraft), num_to_swap)

        # Create new route lists with swapped routes
        new_routes1 = []
        new_routes2 = []

        for idx in range(num_aircraft):
            if idx in swap_indices:
                new_routes1.append(routes2[idx].copy())
                new_routes2.append(routes1[idx].copy())
            else:
                new_routes1.append(routes1[idx].copy())
                new_routes2.append(routes2[idx].copy())

        # Create new chromosomes with swapped routes
        offspring1 = Chromosome(new_routes1)
        offspring2 = Chromosome(new_routes2)

        return offspring1, offspring2

    @timing_decorator
    def extend_route(
        self,
        route: AircraftRoute,
        max_additional_airports: int = 5
    ) -> AircraftRoute:
        """
        Extend an existing aircraft route by adding more airports.

        Args:
            route: Existing route to extend.
            max_additional_airports: Maximum number of airports to add.

        Returns:
            Extended route.
        """
        if route.get_length() < 2:
            return self.initializer.create_random_route()

        extended_route = route.copy()

        # Calculate current time based on route
        current_time = START_TIME
        route_durations = {}
        
        for origin in self.problem_data.get_airport_codes():
            for dest in self.problem_data.get_airport_codes():
                duration = self.problem_data.get_route_duration(origin, dest)
                if duration is not None:
                    route_durations[(origin, dest)] = duration

        schedule = RouteScheduler.compute_schedule(route, route_durations)
        if schedule:
            _, _, current_time = schedule[-1]

        # Try to add more airports
        attempts = 0
        max_attempts = max_additional_airports * 3

        while (
            extended_route.get_length() < route.get_length() + max_additional_airports
            and current_time < END_TIME
            and attempts < max_attempts
        ):
            attempts += 1
            current_airport = extended_route[extended_route.get_length() - 1]

            # Find valid next airports
            valid_next = self.problem_data.get_valid_next_airports(current_airport)

            if not valid_next:
                break

            # Choose random next airport
            next_airport = random.choice(valid_next)
            duration = self.problem_data.get_route_duration(current_airport, next_airport)

            if duration is None:
                break

            arrival_time = current_time + duration

            if arrival_time <= END_TIME:
                extended_route.add_airport(next_airport)
                # Add cooldown if not the last flight
                if arrival_time + COOLDOWN_TIME <= END_TIME:
                    current_time = arrival_time + COOLDOWN_TIME
                else:
                    current_time = arrival_time
            else:
                break

        return extended_route

    @timing_decorator
    def mutate(
        self,
        chromosome: Chromosome,
        mutation_rate: float
    ) -> Chromosome:
        """
        Mutate a chromosome by reinitializing or extending aircraft routes.

        Args:
            chromosome: Chromosome to mutate.
            mutation_rate: Probability of mutating each aircraft.

        Returns:
            Mutated chromosome.
        """
        mutated = chromosome.copy()
        routes = mutated.get_routes()

        for i in range(len(routes)):
            if random.random() < mutation_rate:
                # 60% chance to extend route, 40% chance to reinitialize
                if random.random() < 0.6 and routes[i].get_length() >= 2:
                    routes[i] = self.extend_route(routes[i])
                else:
                    routes[i] = self.initializer.create_random_route()

        return Chromosome(routes)

    @staticmethod
    def calculate_annealed_rate(
        initial_rate: float,
        iteration: int,
        max_iterations: int
    ) -> float:
        """
        Calculate mutation rate with annealing.

        Args:
            initial_rate: Initial mutation rate.
            iteration: Current iteration number.
            max_iterations: Maximum number of iterations.

        Returns:
            Annealed mutation rate.
        """
        if max_iterations == 0:
            return initial_rate

        # Use exponential decay - keeps mutation higher longer
        progress = iteration / max_iterations
        min_rate = 0.05
        return max(min_rate, initial_rate * (0.5 ** (progress * 2)))

