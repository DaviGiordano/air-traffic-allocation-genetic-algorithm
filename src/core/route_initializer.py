"""RouteInitializer creates initial routes."""

import random
from typing import List
from src.models.aircraft_route import AircraftRoute
from src.models.chromosome import Chromosome
from src.models.problem_data import ProblemData
from src.core.route_scheduler import RouteScheduler
from src.config import START_TIME, END_TIME, COOLDOWN_TIME
from src.timing import timing_decorator


class RouteInitializer:
    """Creates initial routes for the genetic algorithm."""

    def __init__(self, problem_data: ProblemData):
        """
        Initialize route initializer.

        Args:
            problem_data: ProblemData containing airport and route information.
        """
        self.problem_data = problem_data

    def create_random_route(
        self,
        min_airports: int = 4,
        max_airports: int = 15
    ) -> AircraftRoute:
        """
        Create a random route with time constraints.

        Args:
            min_airports: Minimum number of airports in route.
            max_airports: Maximum number of airports in route.

        Returns:
            AircraftRoute instance.
        """
        airport_codes = self.problem_data.get_airport_codes()
        
        if len(airport_codes) < 2:
            raise ValueError("Need at least 2 airports")

        # Start with random first airport
        current_time = START_TIME
        route = AircraftRoute([random.choice(airport_codes)])

        # Generate route until time limit is reached
        max_attempts = max_airports * 3
        attempts = 0

        while (
            route.get_length() < max_airports
            and current_time < END_TIME
            and attempts < max_attempts
        ):
            attempts += 1
            current_airport = route[route.get_length() - 1]

            # Find valid next airports
            valid_next = self.problem_data.get_valid_next_airports(current_airport)

            if not valid_next:
                break

            # Choose random next airport
            next_airport = random.choice(valid_next)
            duration = self.problem_data.get_route_duration(current_airport, next_airport)

            if duration is None:
                break

            # Check if we can complete this flight before END_TIME
            arrival_time = current_time + duration

            if arrival_time <= END_TIME:
                route.add_airport(next_airport)
                # Add cooldown if not the last flight
                if arrival_time + COOLDOWN_TIME <= END_TIME:
                    current_time = arrival_time + COOLDOWN_TIME
                else:
                    current_time = arrival_time
            else:
                break

        # Ensure minimum length
        route = self._ensure_minimum_length(route, min_airports)

        return route

    def _ensure_minimum_length(
        self,
        route: AircraftRoute,
        min_airports: int
    ) -> AircraftRoute:
        """
        Ensure route meets minimum length requirement.

        Args:
            route: Route to extend if needed.
            min_airports: Minimum number of airports required.

        Returns:
            Route that meets minimum length (or original if can't extend).
        """
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

        while route.get_length() < min_airports:
            current_airport = route[route.get_length() - 1]
            valid_next = self.problem_data.get_valid_next_airports(current_airport)

            if not valid_next:
                break

            next_airport = random.choice(valid_next)
            duration = self.problem_data.get_route_duration(current_airport, next_airport)

            if duration is None:
                break

            arrival_time = current_time + duration

            if arrival_time <= END_TIME:
                route.add_airport(next_airport)
                # Update time
                if route.get_length() < min_airports and arrival_time + COOLDOWN_TIME <= END_TIME:
                    current_time = arrival_time + COOLDOWN_TIME
                else:
                    current_time = arrival_time
            else:
                break

        return route

    @timing_decorator
    def initialize_chromosome(self, num_aircraft: int = 250) -> Chromosome:
        """
        Create chromosome with random routes.

        Args:
            num_aircraft: Number of aircraft (routes) in chromosome.

        Returns:
            Chromosome instance with random routes.
        """
        chromosome = Chromosome()

        for _ in range(num_aircraft):
            route = self.create_random_route()
            chromosome.add_route(route)

        return chromosome

