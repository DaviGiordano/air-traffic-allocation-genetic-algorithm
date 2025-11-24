"""FitnessEvaluator calculates fitness scores."""

from typing import Dict, List, Tuple
from src.models.chromosome import Chromosome
from src.models.problem_data import ProblemData
from src.core.passenger_allocator import PassengerAllocator
from src.config import FLIGHT_PENALTY, STOP_PENALTY, UNSERVED_PENALTY
from src.timing import timing_decorator


class FitnessEvaluator:
    """Calculates fitness scores for chromosomes."""

    def __init__(self, problem_data: ProblemData):
        """
        Initialize fitness evaluator.

        Args:
            problem_data: ProblemData containing problem information.
        """
        self.problem_data = problem_data
        self.allocator = PassengerAllocator(problem_data)

    @timing_decorator
    def evaluate(self, chromosome: Chromosome) -> Tuple[float, Dict]:
        """
        Evaluate chromosome and calculate fitness score.

        Args:
            chromosome: Chromosome to evaluate.

        Returns:
            Tuple of (fitness_score, statistics_dict).
            statistics_dict contains: unserved_passengers, total_stops,
            total_flights, allocations, unmet_demands, fitness_score.
        """
        # Allocate passengers
        _, allocations, unmet_demands = self.allocator.allocate_passengers(
            chromosome
        )

        # Calculate statistics
        total_stops = sum(stops * passengers for _, _, passengers, _, stops in allocations)
        total_flights = self._count_unique_flights(chromosome, allocations)
        unserved_passengers = sum(pax for _, _, pax in unmet_demands)

        # Calculate fitness score
        fitness_score = self._calculate_fitness_score(
            unserved_passengers, total_stops, total_flights
        )

        statistics = {
            "unserved_passengers": unserved_passengers,
            "total_stops": total_stops,
            "total_flights": total_flights,
            "allocations": allocations,
            "unmet_demands": unmet_demands,
            "fitness_score": fitness_score,
        }

        return fitness_score, statistics

    @staticmethod
    def _calculate_fitness_score(
        unserved_passengers: int,
        total_stops: int,
        total_flights: int
    ) -> float:
        """
        Calculate fitness score from statistics.

        Args:
            unserved_passengers: Number of unserved passengers.
            total_stops: Total stops weighted by passengers.
            total_flights: Number of unique flights.

        Returns:
            Fitness score (lower is better).
        """
        return (
            UNSERVED_PENALTY * unserved_passengers
            + STOP_PENALTY * total_stops
            + FLIGHT_PENALTY * total_flights
        )

    @staticmethod
    def _count_unique_flights(
        chromosome: Chromosome,
        allocations: List[Tuple[str, str, int, int, int]]
    ) -> int:
        """
        Count unique flight legs used in allocations.

        Args:
            chromosome: Chromosome containing routes.
            allocations: List of (origin, dest, passengers, aircraft_id, stops).

        Returns:
            Number of unique flight legs.
        """
        used_flights = set()
        routes = chromosome.get_routes()

        for origin, dest, passengers, aircraft_id, stops in allocations:
            if aircraft_id >= len(routes):
                continue

            route = routes[aircraft_id]
            route_airports = route.get_airports()

            if len(route_airports) < 2:
                continue

            # Find the path from origin to dest in the route
            try:
                origin_idx = route_airports.index(origin)
                dest_idx = route_airports.index(dest)

                if dest_idx > origin_idx:
                    # Add all flight legs used in this path
                    for i in range(origin_idx, dest_idx):
                        leg = (route_airports[i], route_airports[i + 1])
                        used_flights.add(leg)
            except ValueError:
                pass

        return len(used_flights)
