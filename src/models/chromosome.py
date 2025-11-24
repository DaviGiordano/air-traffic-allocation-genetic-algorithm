"""Chromosome model representing a solution (collection of aircraft routes)."""

from typing import List, Optional

from src.models.aircraft_route import AircraftRoute


class Chromosome:
    """Represents a solution (collection of aircraft routes)."""

    def __init__(self, routes: List[AircraftRoute] = None):
        """
        Initialize a chromosome.

        Args:
            routes: List of aircraft routes. If None, creates empty chromosome.
        """
        self._routes = routes.copy() if routes else []
        self._fitness: Optional[float] = None

    def add_route(self, route: AircraftRoute) -> None:
        """
        Add a route to the chromosome.

        Args:
            route: AircraftRoute to add.
        """
        self._routes.append(route)

    def get_routes(self) -> List[AircraftRoute]:
        """
        Get all routes in the chromosome.

        Returns:
            List of AircraftRoute instances.
        """
        return self._routes.copy()

    def get_num_aircraft(self) -> int:
        """
        Get number of aircraft (routes) in the chromosome.

        Returns:
            Number of aircraft.
        """
        return len(self._routes)

    def copy(self) -> "Chromosome":
        """
        Create a copy of this chromosome.

        Returns:
            New Chromosome instance with copied routes.
        """
        copied_routes = [route.copy() for route in self._routes]
        new_chromosome = Chromosome(copied_routes)
        if self._fitness is not None:
            new_chromosome.set_fitness(self._fitness)
        return new_chromosome

    def set_fitness(self, fitness: float) -> None:
        """
        Set fitness score.

        Args:
            fitness: Fitness score value.
        """
        self._fitness = fitness

    def get_fitness(self) -> Optional[float]:
        """
        Get fitness score.

        Returns:
            Fitness score or None if not set.
        """
        return self._fitness

    def __len__(self) -> int:
        """Return number of routes."""
        return len(self._routes)

    def __getitem__(self, index: int) -> AircraftRoute:
        """Get route at index."""
        return self._routes[index]

    def __repr__(self) -> str:
        """String representation."""
        fitness_str = f", fitness={self._fitness}" if self._fitness is not None else ""
        return f"Chromosome({len(self._routes)} routes{fitness_str})"
