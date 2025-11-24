"""PassengerAllocator handles passenger allocation to flights."""

import random
from typing import Dict, List, Tuple, Optional
from src.models.chromosome import Chromosome
from src.models.problem_data import ProblemData
from src.core.route_extractor import RouteExtractor
from src.config import AIRCRAFT_CAPACITY
from src.timing import timing_decorator


class PassengerAllocator:
    """Handles passenger allocation to flights."""

    def __init__(self, problem_data: ProblemData):
        """
        Initialize passenger allocator.

        Args:
            problem_data: ProblemData containing demand information.
        """
        self.problem_data = problem_data

    @timing_decorator
    def allocate_passengers(
        self,
        chromosome: Chromosome
    ) -> Tuple[Dict[int, List[int]], List[Tuple[str, str, int, int, int]], List[Tuple[str, str, int]]]:
        """
        Allocate passengers to flights.

        Args:
            chromosome: Chromosome to allocate passengers for.

        Returns:
            Tuple of (leg_capacities, allocations, unmet_demands)
            - leg_capacities: Dict mapping aircraft_id to list of remaining capacity per leg
            - allocations: List of (origin, dest, passengers, aircraft_id, stops)
            - unmet_demands: List of (origin, dest, passengers) for unserved demand
        """
        # Initialize per-leg capacities
        num_aircraft = chromosome.get_num_aircraft()
        leg_capacities = RouteExtractor.initialize_leg_capacities(
            chromosome, AIRCRAFT_CAPACITY
        )
        route_airports: Dict[int, List[str]] = {}

        # Shuffle demand list
        demand_list = self.problem_data.get_demand_list()
        shuffled_demand = demand_list.copy()
        random.shuffle(shuffled_demand)

        # Track allocations and statistics
        allocations = []
        unmet_demands = []

        # Compute available routes ONCE at the start (capacities updated as we allocate)
        route_map = RouteExtractor.build_route_map(
            chromosome, self.problem_data, leg_capacities, route_airports
        )

        # Process demand
        demand_queue = shuffled_demand.copy()
        max_iterations = len(demand_queue) * 20
        iteration = 0
        od_attempts = {}

        while demand_queue and iteration < max_iterations:
            iteration += 1
            origin, dest, passengers = demand_queue.pop(0)

            # Track attempts for this origin-destination pair
            od_key = (origin, dest)
            od_attempts[od_key] = od_attempts.get(od_key, 0) + 1

            # If we've tried this OD pair too many times, mark as unmet
            if od_attempts[od_key] > num_aircraft * 2:
                unmet_demands.append((origin, dest, passengers))
                continue

            # Find best route for this demand
            if od_key not in route_map or not route_map[od_key]:
                unmet_demands.append((origin, dest, passengers))
                continue

            # Get best route (first in sorted list)
            best_route = route_map[od_key][0]
            aircraft_id, stops, total_time, capacity_remaining, start_idx, end_idx = best_route

            # Check current capacity for the specific segment
            segment_capacity = RouteExtractor._segment_capacity(
                leg_capacities, aircraft_id, start_idx, end_idx
            )

            if segment_capacity > 0:
                # Allocate passengers (can be partial allocation)
                passengers_to_allocate = min(passengers, segment_capacity)

                allocations.append(
                    (origin, dest, passengers_to_allocate, aircraft_id, stops)
                )

                # Reset attempt counter since we made progress
                od_attempts[od_key] = 0

                # Update per-leg capacities for the flown segment
                for leg_idx in range(start_idx, end_idx):
                    if leg_idx < len(leg_capacities.get(aircraft_id, [])):
                        leg_capacities[aircraft_id][leg_idx] = max(
                            0, leg_capacities[aircraft_id][leg_idx] - passengers_to_allocate
                        )

                # Update route map with new per-segment capacities
                RouteExtractor.update_capacity_in_map(
                    route_map, aircraft_id, leg_capacities
                )

                # If demand was only partially satisfied, put remainder back in queue
                remaining_passengers = passengers - passengers_to_allocate
                if remaining_passengers > 0:
                    demand_queue.insert(0, (origin, dest, remaining_passengers))
            else:
                # No capacity available, put back at front of queue
                demand_queue.insert(0, (origin, dest, passengers))

        return leg_capacities, allocations, unmet_demands

    @staticmethod
    def find_best_route(
        origin: str,
        dest: str,
        route_map: Dict[Tuple[str, str], List[Tuple[int, int, int, int, int, int]]]
    ) -> Optional[Tuple[int, int, int, int, int, int]]:
        """
        Find best route for an origin-destination pair.

        Args:
            origin: Origin airport code.
            dest: Destination airport code.
            route_map: Dictionary of available routes.

        Returns:
            Best route tuple (aircraft_id, stops, total_time, capacity, start_idx, end_idx) or None.
        """
        od_key = (origin, dest)
        if od_key not in route_map or not route_map[od_key]:
            return None
        return route_map[od_key][0]
