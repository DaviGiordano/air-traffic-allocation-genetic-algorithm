"""RouteExtractor extracts origin-destination pairs from routes."""

from typing import List, Dict, Tuple
from src.models.aircraft_route import AircraftRoute
from src.models.chromosome import Chromosome
from src.models.problem_data import ProblemData
from src.core.route_scheduler import RouteScheduler
from src.config import START_TIME, COOLDOWN_TIME
from src.timing import timing_decorator


class RouteExtractor:
    """Extracts origin-destination pairs from routes."""

    @staticmethod
    @timing_decorator
    def extract_od_pairs(
        route: AircraftRoute,
        route_durations: Dict[Tuple[str, str], int]
    ) -> List[Tuple[str, str, int, int, int, int, int]]:
        """
        Extract all possible origin-destination routes from an aircraft route.

        Args:
            route: AircraftRoute to extract from.
            route_durations: Dictionary mapping (origin, dest) to duration.

        Returns:
            List of (origin, dest, stops, total_time, departure_time, start_idx, end_idx) tuples.
        """
        if route.get_length() < 2:
            return []

        airports_full = route.get_airports()
        schedule = RouteScheduler.compute_schedule(route, route_durations)

        if not schedule:
            return []

        # Only consider the portion of the route that fits in the time window
        max_leg_idx = len(schedule)  # number of legs scheduled
        airports = airports_full[: max_leg_idx + 1]

        routes = []

        # Extract direct and multi-stop routes within the scheduled window
        for i in range(len(airports)):
            for j in range(i + 1, len(airports)):
                origin = airports[i]
                dest = airports[j]

                # Calculate total time and stops
                stops = j - i - 1
                total_time = 0
                departure_time = START_TIME

                # Find departure time for origin
                if i == 0:
                    departure_time = START_TIME
                else:
                    if i - 1 < len(schedule):
                        _, _, arr_time = schedule[i - 1]
                        if i - 1 < len(airports) - 2:
                            departure_time = arr_time + COOLDOWN_TIME
                        else:
                            departure_time = arr_time

                # Calculate total travel time
                valid = True
                current_time = departure_time
                for k in range(i, j):
                    leg_origin = airports[k]
                    leg_dest = airports[k + 1]
                    leg = (leg_origin, leg_dest)

                    if leg not in route_durations:
                        valid = False
                        break

                    duration = route_durations[leg]
                    total_time += duration
                    current_time += duration

                    if k < j - 1:
                        total_time += COOLDOWN_TIME
                        current_time += COOLDOWN_TIME

                if valid:
                    routes.append(
                        (origin, dest, stops, total_time, departure_time, i, j)
                    )

        return routes

    @staticmethod
    @timing_decorator
    def build_route_map(
        chromosome: Chromosome,
        problem_data: ProblemData,
        leg_capacities: Dict[int, List[int]],
        route_airports: Dict[int, List[str]]
    ) -> Dict[Tuple[str, str], List[Tuple[int, int, int, int, int, int]]]:
        """
        Build route availability map for all origin-destination pairs.

        Args:
            chromosome: Chromosome to extract routes from.
            problem_data: ProblemData containing route durations.
            leg_capacities: Dictionary mapping aircraft_id to list of remaining capacity per leg.
            route_airports: Dictionary to populate with aircraft_id -> list of airports for later updates.

        Returns:
            Dictionary mapping (origin, dest) to list of
            (aircraft_id, stops, total_time, capacity_remaining, start_idx, end_idx).
            Routes are sorted by (stops, total_time).
        """
        route_map = {}
        route_durations = {}
        
        # Build route_durations dict from problem_data
        for origin in problem_data.get_airport_codes():
            for dest in problem_data.get_airport_codes():
                duration = problem_data.get_route_duration(origin, dest)
                if duration is not None:
                    route_durations[(origin, dest)] = duration

        for aircraft_id, route in enumerate(chromosome.get_routes()):
            airports = route.get_airports()
            route_airports[aircraft_id] = airports
            if len(airports) < 2:
                continue

            extracted_routes = RouteExtractor.extract_od_pairs(route, route_durations)

            for origin, dest, stops, total_time, _, start_idx, end_idx in extracted_routes:
                key = (origin, dest)
                capacity = RouteExtractor._segment_capacity(
                    leg_capacities, aircraft_id, start_idx, end_idx
                )

                if capacity <= 0:
                    continue

                if key not in route_map:
                    route_map[key] = []

                route_map[key].append(
                    (aircraft_id, stops, total_time, capacity, start_idx, end_idx)
                )

        # Sort routes by (stops, total_time) for each origin-destination pair
        for key in route_map:
            route_map[key].sort(key=lambda x: (x[1], x[2], x[-1]))

        return route_map

    @staticmethod
    @timing_decorator
    def update_capacity_in_map(
        route_map: Dict[Tuple[str, str], List[Tuple[int, int, int, int, int, int]]],
        aircraft_id: int,
        leg_capacities: Dict[int, List[int]]
    ) -> None:
        """
        Update capacities for all routes involving a specific aircraft using per-leg capacities.

        Args:
            route_map: Dictionary of available routes.
            aircraft_id: ID of aircraft to update.
            leg_capacities: Dictionary of remaining capacity per leg for each aircraft.
        """
        keys_to_delete = []
        for key in route_map:
            updated_routes = []
            for route in route_map[key]:
                aid, stops, total_time, _, start_idx, end_idx = route
                if aid == aircraft_id:
                    capacity = RouteExtractor._segment_capacity(
                        leg_capacities, aircraft_id, start_idx, end_idx
                    )
                    if capacity > 0:
                        updated_routes.append(
                            (aid, stops, total_time, capacity, start_idx, end_idx)
                        )
                else:
                    updated_routes.append(route)
            if updated_routes:
                updated_routes.sort(key=lambda x: (x[1], x[2]))
                route_map[key] = updated_routes
            else:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            route_map.pop(key, None)

    @staticmethod
    def remove_aircraft_from_map(
        route_map: Dict[Tuple[str, str], List[Tuple[int, int, int, int, int, int]]],
        aircraft_id: int
    ) -> None:
        """
        Remove all routes involving a specific aircraft from the route map.

        Args:
            route_map: Dictionary of available routes.
            aircraft_id: ID of aircraft to remove.
        """
        for key in route_map:
            route_map[key] = [
                route for route in route_map[key]
                if route[0] != aircraft_id
            ]

    @staticmethod
    def initialize_leg_capacities(chromosome: Chromosome, default_capacity: int) -> Dict[int, List[int]]:
        """
        Initialize per-leg capacities for each aircraft.

        Args:
            chromosome: Chromosome with routes.
            default_capacity: Initial capacity per leg.

        Returns:
            Dictionary mapping aircraft_id to list of capacities per leg.
        """
        leg_capacities: Dict[int, List[int]] = {}
        for aircraft_id, route in enumerate(chromosome.get_routes()):
            leg_count = max(route.get_length() - 1, 0)
            leg_capacities[aircraft_id] = [default_capacity for _ in range(leg_count)]
        return leg_capacities

    @staticmethod
    def _segment_capacity(
        leg_capacities: Dict[int, List[int]], aircraft_id: int, start_idx: int, end_idx: int
    ) -> int:
        """
        Compute available capacity for a segment between start and end indices.

        Args:
            leg_capacities: Remaining capacities per leg.
            aircraft_id: Aircraft identifier.
            start_idx: Start airport index in route.
            end_idx: End airport index (exclusive of last airport index).

        Returns:
            Minimum capacity across all legs in the segment.
        """
        legs = leg_capacities.get(aircraft_id, [])
        if start_idx >= end_idx or start_idx < 0 or end_idx > len(legs):
            return 0
        return min(legs[start_idx:end_idx])
