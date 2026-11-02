# 1. Identify available parcels.
# 2. Calculate the estimated arrival time for each parcel, including the 30-minute departure delay.
# 3. Prioritise parcels that can still be delivered within their preferred windows.
# 4. Among those parcels, consider the earliest deadlines first.
# 5. Check capacity, vehicle range and the 18:00 return constraint before adding each parcel.
# 6. Continue considering late parcels where appropriate, rather than automatically ignoring them.

from typing import Dict, List

from simulator.models import Parcel, SimulationContext

HUB = "HUB"


def dispatch(
    parcel: Dict[str, Parcel],
    context: SimulationContext
) -> List[str]:

    distances = context["travel_distance"]

    departure_time = (
        context["current_time"]
        + context["departure_delay"]
    )

    capacity = context["capacity"]
    max_distance = context["max_trip_distance_km"]
    return_cutoff = context["return_cutoff"]

    # Step 1: Find all available parcels
    waiting = [
        parcel_id
        for parcel_id, record in parcel.items()
        if record["vehicle_assigned"] is None
        and record["delivery_time"] is None
    ]

    # Step 2: Initialise route information
    route: List[str] = []
    load = 0.0
    travelled = 0.0
    current_location = HUB

    # Step 3: Build the route one parcel at a time
    while waiting:

        feasible_on_time = []
        feasible_late = []

        for parcel_id in waiting:

            record = parcel[parcel_id]

            # Check capacity
            if load + record["size"] > capacity:
                continue

            destination = record["delivery_location_id"]

            # Distance from current stop to destination
            leg_distance = distances[
                current_location
            ][destination]

            # Total distance to reach this parcel
            new_distance = travelled + leg_distance

            # Include distance to return to hub
            total_trip_distance = (
                new_distance
                + distances[destination][HUB]
            )

            # Check vehicle range
            if total_trip_distance > max_distance:
                continue

            # At 60 km/h, distance in km equals
            # travel time in minutes
            estimated_arrival = (
                departure_time + new_distance
            )

            estimated_return = (
                departure_time + total_trip_distance
            )

            # Check mandatory return time
            if estimated_return > return_cutoff:
                continue

            deadline = record["delivery_window_end"]
            window_start = record["delivery_window_start"]

            candidate = (
                deadline,
                parcel_id,
                destination,
                new_distance
            )

            # Step 4: Classify delivery feasibility
            if (
                window_start
                <= estimated_arrival
                <= deadline
            ):
                feasible_on_time.append(candidate)
            else:
                feasible_late.append(candidate)

        # Step 5: Select the best available parcel
        if feasible_on_time:
            # Earliest deadline among on-time parcels
            feasible_on_time.sort()
            selected = feasible_on_time[0]

        elif feasible_late:
            # Fallback: deliver even if outside window
            feasible_late.sort()
            selected = feasible_late[0]

        else:
            # No additional parcel can fit the route
            break

        # Step 6: Update route
        _, selected_id, destination, new_distance = selected

        route.append(selected_id)
        load += parcel[selected_id]["size"]
        travelled = new_distance
        current_location = destination

        waiting.remove(selected_id)

    return route
