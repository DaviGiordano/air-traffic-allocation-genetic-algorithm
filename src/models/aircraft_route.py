"""AircraftRoute model representing a single aircraft route."""

from typing import Dict, List, Tuple


class AircraftRoute:
    """Represents a single aircraft route (sequence of airports)."""

    def __init__(self, airports: List[str] = None):
        """
        Initialize an aircraft route.

        Args:
            airports: List of airport codes. If None, creates empty route.
        """
        self._airports = airports.copy() if airports else []

    def add_airport(self, airport: str) -> None:
        """
        Add an airport to the route.

        Args:
            airport: Airport code to add.
        """
        self._airports.append(airport)

    def get_flight_legs(self) -> List[Tuple[str, str]]:
        """
        Get list of flight legs (origin, dest) tuples.

        Returns:
            List of (origin, dest) tuples.
        """
        legs = []
        for i in range(len(self._airports) - 1):
            legs.append((self._airports[i], self._airports[i + 1]))
        return legs

    def get_length(self) -> int:
        """
        Get number of airports in the route.

        Returns:
            Number of airports.
        """
        return len(self._airports)

    def get_airports(self) -> List[str]:
        """
        Get list of airports in the route.

        Returns:
            List of airport codes.
        """
        return self._airports.copy()

    def copy(self) -> "AircraftRoute":
        """
        Create a copy of this route.

        Returns:
            New AircraftRoute instance with same airports.
        """
        return AircraftRoute(self._airports)

    def is_valid(self, route_durations: Dict[Tuple[str, str], int]) -> bool:
        """
        Check if route is valid (all flight legs exist in route_durations).

        Args:
            route_durations: Dictionary mapping (origin, dest) to duration.

        Returns:
            True if all flight legs are valid, False otherwise.
        """
        if len(self._airports) < 2:
            return False

        for i in range(len(self._airports) - 1):
            leg = (self._airports[i], self._airports[i + 1])
            if leg not in route_durations:
                return False
        return True

    def __len__(self) -> int:
        """Return number of airports."""
        return len(self._airports)

    def __getitem__(self, index: int) -> str:
        """Get airport at index."""
        return self._airports[index]

    def __repr__(self) -> str:
        """String representation."""
        return f"AircraftRoute({self._airports})"
