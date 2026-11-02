# Heuristics Earliest Deadline First (EDF)

# 1.Identify parcels that have arrived and have not been assigned or delivered.
# 2.Sort them by their delivery-window end times, earliest first.
# 3.Starting with an empty vehicle route, consider parcels in that order.
# 4.Add a parcel only if the resulting route satisfies capacity, distance and 18:00 return constraints.
# 5.Return the selected parcel IDs in delivery order.
# 6.If no valid parcel can be selected, return an empty list.


from typing import Dict, List

from simulator.models import Parcel, SimulationContext

HUB = "HUB"


def dispatch(parcel: Dict[str, Parcel],
             context: SimulationContext) -> List[str]:

    distances = context["travel_distance"]
    departure = context["current_time"] + context["departure_delay"]
    max_distance = context["max_trip_distance_km"]

    # 1. Identify parcels that are waiting
    waiting = sorted(
        (
            parcel_id
            for parcel_id, record in parcel.items()
            if record["vehicle_assigned"] is None
            and record["delivery_time"] is None
        ),
        key=lambda parcel_id: (
            parcel[parcel_id]["delivery_window_end"],
            parcel_id
        )
    )

    # 2. Initialise the vehicle route
    route: List[str] = []
    load = 0.0
    travelled = 0.0
    location = HUB

    # 3. Consider parcels in deadline order
    for parcel_id in waiting:
        record = parcel[parcel_id]

        # Check vehicle capacity
        if load + record["size"] > context["capacity"]:
            continue

        destination = record["delivery_location_id"]

        # Distance travelled if this parcel is added
        trip_distance = (
            travelled + distances[location][destination]
        )

        # Include return journey to the hub
        round_trip = (
            trip_distance + distances[destination][HUB]
        )

        # Check vehicle range and return deadline
        if (
            round_trip > max_distance
            or departure + round_trip > context["return_cutoff"]
        ):
            continue

        # Accept parcel
        route.append(parcel_id)
        load += record["size"]
        travelled = trip_distance
        location = destination

    return route
