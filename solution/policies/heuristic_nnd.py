"""Greedy nearest-neighbor dispatch using a priority queue."""

import heapq
from typing import Dict, List

from simulator.models import Parcel, SimulationContext

HUB = "HUB"

def dispatch(
    parcel: Dict[str, Parcel],
    context: SimulationContext,
) -> List[str]:
    distances = context["travel_distance"]
    departure_time = context["current_time"] + context["departure_delay"]
    capacity = context["capacity"]
    max_distance = context["max_trip_distance_km"]
    return_cutoff = context["return_cutoff"]

    # Only consider parcels that are waiting to be assigned.
    waiting = set()  # Start with an empty set of parcel IDs

    for parcel_id, record in parcel.items():
        if record["vehicle_assigned"] is None and record["delivery_time"] is None:
            waiting.add(parcel_id)

    # Initialize the route, load, travelled distance, and current location.
    route: List[str] = []
    load = 0.0
    travelled = 0.0
    current_location = HUB

    # Use a priority queue to select the next parcel to deliver based on the nearest neighbor heuristic
    while waiting:
        # A min-heap: lower priority values are selected first.
        candidates = []

        for parcel_id in waiting:
            record = parcel[parcel_id]

            # Check the vehicle's capacity.
            if load + record["size"] > capacity:
                continue

            destination = record["delivery_location_id"]
            leg_distance = distances[current_location][destination]
            new_distance = travelled + leg_distance

            # Include the return journey when checking range and cutoff.
            total_trip_distance = new_distance + distances[destination][HUB]
            estimated_return = departure_time + total_trip_distance

            if total_trip_distance > max_distance:
                continue
            if estimated_return > return_cutoff:
                continue

            # At 60 km/h, kilometres travelled equal travel time in minutes.
            estimated_arrival = departure_time + new_distance
            on_time = (
                record["delivery_window_start"]
                <= estimated_arrival
                <= record["delivery_window_end"]
            )

            # Priority: predicted on-time first, then shortest next leg,
            # then earliest deadline, then parcel ID for a consistent tie-break.
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