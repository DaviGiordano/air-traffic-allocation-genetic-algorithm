"""RouteScheduler handles time calculations and scheduling."""

from typing import List, Tuple
from src.models.aircraft_route import AircraftRoute
from src.config import START_TIME, END_TIME, COOLDOWN_TIME


class RouteScheduler:
    """Handles time calculations and scheduling for aircraft routes."""

    @staticmethod
    def compute_schedule(route: AircraftRoute, route_durations: dict) -> List[Tuple[int, str, int]]:
        """
        Calculate flight schedule for a route.

        Args:
            route: AircraftRoute to schedule.
            route_durations: Dictionary mapping (origin, dest) to duration.

        Returns:
            List of (departure_time, airport, arrival_time) tuples.
        """
        if route.get_length() < 2:
            return []

        schedule = []
        current_time = START_TIME
        airports = route.get_airports()

        for i in range(len(airports) - 1):
            origin = airports[i]
            dest = airports[i + 1]
            leg = (origin, dest)

            if leg not in route_durations:
                break

            duration = route_durations[leg]
            departure_time = current_time
            arrival_time = current_time + duration

            schedule.append((departure_time, dest, arrival_time))

            # Add cooldown if not the last flight
            if i < len(airports) - 2:
                current_time = arrival_time + COOLDOWN_TIME
            else:
                current_time = arrival_time

        return schedule

    @staticmethod
    def can_add_flight(
        current_time: int,
        origin: str,
        dest: str,
        route_durations: dict
    ) -> bool:
        """
        Check if a flight can be added within the time window.

        Args:
            current_time: Current time in minutes from midnight.
            origin: Origin airport code.
            dest: Destination airport code.
            route_durations: Dictionary mapping (origin, dest) to duration.

        Returns:
            True if flight can be added, False otherwise.
        """
        leg = (origin, dest)
        if leg not in route_durations:
            return False

        duration = route_durations[leg]
        arrival_time = current_time + duration
        return arrival_time <= END_TIME

    @staticmethod
    def calculate_arrival_time(departure_time: int, duration: int) -> int:
        """
        Calculate arrival time.

        Args:
            departure_time: Departure time in minutes from midnight.
            duration: Flight duration in minutes.

        Returns:
            Arrival time in minutes from midnight.
        """
        return departure_time + duration

    @staticmethod
    def add_cooldown_time(arrival_time: int) -> int:
        """
        Add cooldown time to arrival time.

        Args:
            arrival_time: Arrival time in minutes from midnight.

        Returns:
            Time after cooldown in minutes from midnight.
        """
        return arrival_time + COOLDOWN_TIME

    @staticmethod
    def calculate_route_time(route: AircraftRoute, route_durations: dict) -> int:
        """
        Calculate total time for a route including flights and cooldowns.

        Args:
            route: AircraftRoute to calculate time for.
            route_durations: Dictionary mapping (origin, dest) to duration.

        Returns:
            Total time in minutes from START_TIME.
        """
        if route.get_length() < 2:
            return 0

        current_time = START_TIME
        airports = route.get_airports()

        for i in range(len(airports) - 1):
            leg = (airports[i], airports[i + 1])
            if leg not in route_durations:
                break

            duration = route_durations[leg]
            arrival_time = current_time + duration

            if i < len(airports) - 2:
                current_time = arrival_time + COOLDOWN_TIME
            else:
                current_time = arrival_time

        return current_time - START_TIME

