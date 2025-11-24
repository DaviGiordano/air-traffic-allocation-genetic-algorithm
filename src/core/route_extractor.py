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
    ) -> List[Tuple[str, str, int, int, int]]:
        """
        Extract all possible origin-destination routes from an aircraft route.

        Args:
            route: AircraftRoute to extract from.
            route_durations: Dictionary mapping (origin, dest) to duration.

        Returns:
            List of (origin, dest, stops, total_time, departure_time) tuples.
        """
        if route.get_length() < 2:
            return []

        airports = route.get_airports()
        schedule = RouteScheduler.compute_schedule(route, route_durations)

        if not schedule:
            return []

        routes = []

        # Extract direct and multi-stop routes
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
                    routes.append((origin, dest, stops, total_time, departure_time))

        return routes

    @staticmethod
    @timing_decorator
    def build_route_map(
        chromosome: Chromosome,
        problem_data: ProblemData,
        aircraft_capacity: Dict[int, int]
    ) -> Dict[Tuple[str, str], List[Tuple[int, int, int, int]]]:
        """
        Build route availability map for all origin-destination pairs.

        Args:
            chromosome: Chromosome to extract routes from.
            problem_data: ProblemData containing route durations.
            aircraft_capacity: Dictionary mapping aircraft_id to remaining capacity.

        Returns:
            Dictionary mapping (origin, dest) to list of
            (aircraft_id, stops, total_time, capacity_remaining).
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
            if aircraft_capacity.get(aircraft_id, 0) <= 0:
                continue

            extracted_routes = RouteExtractor.extract_od_pairs(route, route_durations)

            for origin, dest, stops, total_time, _ in extracted_routes:
                key = (origin, dest)
                capacity = aircraft_capacity.get(aircraft_id, 0)

                if key not in route_map:
                    route_map[key] = []

                route_map[key].append((aircraft_id, stops, total_time, capacity))

        # Sort routes by (stops, total_time) for each origin-destination pair
        for key in route_map:
            route_map[key].sort(key=lambda x: (x[1], x[2]))

        return route_map

    @staticmethod
    @timing_decorator
    def update_capacity_in_map(
        route_map: Dict[Tuple[str, str], List[Tuple[int, int, int, int]]],
        aircraft_id: int,
        new_capacity: int
    ) -> None:
        """
        Update capacity for all routes involving a specific aircraft.

        Args:
            route_map: Dictionary of available routes.
            aircraft_id: ID of aircraft to update.
            new_capacity: New capacity value.
        """
        for key in route_map:
            updated_routes = []
            for route in route_map[key]:
                if route[0] == aircraft_id:
                    updated_routes.append((route[0], route[1], route[2], new_capacity))
                else:
                    updated_routes.append(route)
            route_map[key] = updated_routes
            route_map[key].sort(key=lambda x: (x[1], x[2]))

    @staticmethod
    def remove_aircraft_from_map(
        route_map: Dict[Tuple[str, str], List[Tuple[int, int, int, int]]],
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

