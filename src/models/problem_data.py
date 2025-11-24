"""ProblemData model holding all problem data."""

from typing import Dict, List, Optional, Tuple


class ProblemData:
    """Holds all problem data (airports, routes, demand)."""

    def __init__(
        self,
        airport_codes: List[str],
        route_durations: Dict[Tuple[str, str], int],
        demand_list: List[Tuple[str, str, int]],
    ):
        """
        Initialize problem data.

        Args:
            airport_codes: List of airport codes.
            route_durations: Dictionary mapping (origin, dest) to duration in minutes.
            demand_list: List of (origin, dest, passengers) tuples.
        """
        self._airport_codes = airport_codes.copy()
        self._route_durations = route_durations.copy()
        self._demand_list = demand_list.copy()

    def get_airport_codes(self) -> List[str]:
        """
        Get list of airport codes.

        Returns:
            List of airport codes.
        """
        return self._airport_codes.copy()

    def get_route_duration(self, origin: str, dest: str) -> Optional[int]:
        """
        Get duration for a route.

        Args:
            origin: Origin airport code.
            dest: Destination airport code.

        Returns:
            Duration in minutes, or None if route doesn't exist.
        """
        return self._route_durations.get((origin, dest))

    def get_demand_list(self) -> List[Tuple[str, str, int]]:
        """
        Get list of demand tuples.

        Returns:
            List of (origin, dest, passengers) tuples.
        """
        return self._demand_list.copy()

    def get_valid_next_airports(self, current_airport: str) -> List[str]:
        """
        Get airports reachable from current airport.

        Args:
            current_airport: Current airport code.

        Returns:
            List of airport codes that can be reached from current airport.
        """
        valid = []
        for airport in self._airport_codes:
            if airport != current_airport:
                if (current_airport, airport) in self._route_durations:
                    valid.append(airport)
        return valid

    def has_route(self, origin: str, dest: str) -> bool:
        """
        Check if a route exists between two airports.

        Args:
            origin: Origin airport code.
            dest: Destination airport code.

        Returns:
            True if route exists, False otherwise.
        """
        return (origin, dest) in self._route_durations

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ProblemData({len(self._airport_codes)} airports, "
            f"{len(self._route_durations)} routes, "
            f"{len(self._demand_list)} demand pairs)"
        )
