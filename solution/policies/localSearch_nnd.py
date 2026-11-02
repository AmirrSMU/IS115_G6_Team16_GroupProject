"""Greedy nearest-neighbor dispatch improved with local search."""

import heapq
from typing import Dict, List, Set, Tuple

from simulator.models import Parcel, SimulationContext

HUB = "HUB"
MAX_LOCAL_SEARCH_STEPS = 50


def dispatch(
    parcel: Dict[str, Parcel],
    context: SimulationContext,
) -> List[str]:
    """Build a greedy route, then try small changes to improve it."""

    available = {
        parcel_id
        for parcel_id, record in parcel.items()
        if record["vehicle_assigned"] is None
        and record["delivery_time"] is None
    }

    route = build_greedy_route(parcel, context, available)
    return improve_route(route, available, parcel, context)


def build_greedy_route(
    parcel: Dict[str, Parcel],
    context: SimulationContext,
    available: Set[str],
) -> List[str]:
    """Choose on-time feasible parcels first, then the closest next stop."""

    distances = context["travel_distance"]
    departure_time = context["current_time"] + context["departure_delay"]
    capacity = context["capacity"]
    max_distance = context["max_trip_distance_km"]
    return_cutoff = context["return_cutoff"]

    waiting = set(available)
    route: List[str] = []
    load = 0.0
    travelled = 0.0
    current_location = HUB

    while waiting:
        candidates = []

        for parcel_id in waiting:
            record = parcel[parcel_id]

            if load + record["size"] > capacity:
                continue

            destination = record["delivery_location_id"]
            leg_distance = distances[current_location][destination]
            new_distance = travelled + leg_distance
            total_trip_distance = new_distance + distances[destination][HUB]
            estimated_return = departure_time + total_trip_distance

            if total_trip_distance > max_distance:
                continue
            if estimated_return > return_cutoff:
                continue

            estimated_arrival = departure_time + new_distance
            on_time = (
                record["delivery_window_start"]
                <= estimated_arrival
                <= record["delivery_window_end"]
            )

            # heapq is a min-heap: smaller values are selected first.
            heapq.heappush(
                candidates,
                (
                    0 if on_time else 1,
                    leg_distance,
                    record["delivery_window_end"],
                    parcel_id,
                    destination,
                    new_distance,
                ),
            )

        if not candidates:
            break

        _, _, _, selected_id, destination, new_distance = heapq.heappop(candidates)

        route.append(selected_id)
        load += parcel[selected_id]["size"]
        travelled = new_distance
        current_location = destination
        waiting.remove(selected_id)

    return route


def improve_route(
    route: List[str],
    available: Set[str],
    parcel: Dict[str, Parcel],
    context: SimulationContext,
) -> List[str]:
    """Try small route changes, keeping each change that improves the score."""

    current_route = route[:]
    current_score = score_route(current_route, parcel, context)

    for _ in range(MAX_LOCAL_SEARCH_STEPS):
        selected = set(current_route)
        alternatives = sorted(available - selected)
        improved = False

        # Try replacing one selected parcel with one waiting parcel.
        for index in range(len(current_route)):
            for replacement_id in alternatives:
                candidate = current_route[:]
                candidate[index] = replacement_id

                if route_is_feasible(candidate, parcel, context):
                    candidate_score = score_route(candidate, parcel, context)
                    if candidate_score > current_score:
                        current_route = candidate
                        current_score = candidate_score
                        improved = True
                        break

            if improved:
                break

        # Try inserting a waiting parcel at each position.
        if not improved:
            for replacement_id in alternatives:
                for index in range(len(current_route) + 1):
                    candidate = current_route[:]
                    candidate.insert(index, replacement_id)

                    if route_is_feasible(candidate, parcel, context):
                        candidate_score = score_route(candidate, parcel, context)
                        if candidate_score > current_score:
                            current_route = candidate
                            current_score = candidate_score
                            improved = True
                            break

                if improved:
                    break

        # Try removing a parcel. This may let later stops become on time.
        if not improved:
            for index in range(len(current_route)):
                candidate = current_route[:]
                candidate.pop(index)

                if route_is_feasible(candidate, parcel, context):
                    candidate_score = score_route(candidate, parcel, context)
                    if candidate_score > current_score:
                        current_route = candidate
                        current_score = candidate_score
                        improved = True
                        break

        # Try swapping the order of two stops.
        if not improved:
            for first in range(len(current_route)):
                for second in range(first + 1, len(current_route)):
                    candidate = current_route[:]
                    candidate[first], candidate[second] = (
                        candidate[second],
                        candidate[first],
                    )

                    if route_is_feasible(candidate, parcel, context):
                        candidate_score = score_route(candidate, parcel, context)
                        if candidate_score > current_score:
                            current_route = candidate
                            current_score = candidate_score
                            improved = True
                            break

                if improved:
                    break

        # Stop when none of the changes improved the route.
        if not improved:
            break

    return current_route


def route_distance(
    route: List[str],
    parcel: Dict[str, Parcel],
    context: SimulationContext,
) -> float:
    """Calculate route distance, including the return to the hub."""

    distances = context["travel_distance"]
    location = HUB
    total_distance = 0.0

    for parcel_id in route:
        destination = parcel[parcel_id]["delivery_location_id"]
        total_distance += distances[location][destination]
        location = destination

    total_distance += distances[location][HUB]
    return total_distance


def route_is_feasible(
    route: List[str],
    parcel: Dict[str, Parcel],
    context: SimulationContext,
) -> bool:
    """Check that the route obeys capacity, range, and return-time limits."""

    if len(route) != len(set(route)):
        return False

    if any(parcel_id not in parcel for parcel_id in route):
        return False

    total_load = sum(parcel[parcel_id]["size"] for parcel_id in route)
    if total_load > context["capacity"]:
        return False

    total_distance = route_distance(route, parcel, context)
    if total_distance > context["max_trip_distance_km"]:
        return False

    departure_time = context["current_time"] + context["departure_delay"]
    return_time = departure_time + total_distance
    if return_time > context["return_cutoff"]:
        return False

    return True


def score_route(
    route: List[str],
    parcel: Dict[str, Parcel],
    context: SimulationContext,
) -> Tuple[int, int, float]:
    """Prefer more on-time parcels, then more parcels, then a shorter route."""

    distances = context["travel_distance"]
    departure_time = context["current_time"] + context["departure_delay"]

    on_time_count = 0
    travelled = 0.0
    location = HUB

    for parcel_id in route:
        record = parcel[parcel_id]
        destination = record["delivery_location_id"]

        travelled += distances[location][destination]
        estimated_arrival = departure_time + travelled

        if (
            record["delivery_window_start"]
            <= estimated_arrival
            <= record["delivery_window_end"]
        ):
            on_time_count += 1

        location = destination

    total_distance = route_distance(route, parcel, context)

    # Tuple comparison makes on-time count the main goal.
    return on_time_count, -total_distance