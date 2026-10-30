"""Calculate performance metrics from one simulation run's event log."""

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from simulator.loaders import day_input_paths

#     parcels: List[Dict[str, str]],
#     distances: List[Dict[str, str]],
#     config: Dict[str, Any],
#     events: List[Dict[str, Any]],
# ) -> Dict[str, Any]:
#     """Return a JSON-serializable dictionary for the chosen performance metric.

#     parcels and distances are the rows of the day's CSV files, config is the
#     contents of config.json, and events are the records from the run's log.
#     CSV values are strings, so convert them before calculating. In particular,
#     parcel times are "HH:MM" strings while event times are minutes after
#     midnight: "17:00" is 17 * 60 = 1020.
#     """

#     # Illustration only: replace or extend this with your chosen metric.
#     number_of_trips = 0
#     for event in events:
#         if event["event_type"] == "hub_departure":
#             number_of_trips += 1
#     return {"number_of_trips": number_of_trips}

def calculate_metrics(parcels, distances, config, events):
    """Calculate the on-time delivery rate (OTDR)."""

    # Step 1: Count all parcels arriving during the day
    total_parcels = len(parcels)

    # Step 2: Store parcel records by their unique ID
    parcel_lookup = {
        p["parcel_id"]: p
        for p in parcels
    }

    # Step 3: Track how many parcels are delivered on time
    on_time_deliveries = 0
    delivered_ids = set()

    # Step 4: Examine the simulation's delivery events
    for event in events:

        if event["event_type"] != "delivery":
            continue

        parcel_id = event["parcel_id"]

        # Avoid counting the same parcel twice
        if parcel_id in delivered_ids:
            continue

        parcel = parcel_lookup[parcel_id]
        delivered_ids.add(parcel_id)

        # Actual delivery time is already in minutes
        delivery_time = float(event["time"])

        # Convert HH:MM into minutes after midnight
        start_h, start_m = map(
            int, parcel["delivery_window_start"].split(":")
        )

        end_h, end_m = map(
            int, parcel["delivery_window_end"].split(":")
        )

        window_start = start_h * 60 + start_m
        window_end = end_h * 60 + end_m

        # Step 5: Check whether delivery was on time
        if window_start <= delivery_time <= window_end:
            on_time_deliveries += 1

    # Step 6: Calculate the final metric
    otdr = (
        on_time_deliveries / total_parcels * 100
        if total_parcels > 0
        else 0.0
    )

    return {
        "total_parcels": total_parcels,
        "delivered_parcels": len(delivered_ids),
        "on_time_deliveries": on_time_deliveries,
        "otdr_percent": round(otdr, 2)
    }



def main(argv: Optional[List[str]] = None) -> int:
    """Load one day's inputs and event log, then write the metrics report."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"),
                        help="directory containing dist.csv, config.json and demand/")
    parser.add_argument("--day", required=True, help="day identifier, for example day_001")
    parser.add_argument("--log", type=Path, required=True,
                        help="event log from a simulator run")
    parser.add_argument("--output", type=Path,
                        help="JSON report (default: metrics.json beside the selected log)")
    args = parser.parse_args(argv)
    try:
        parcel_path, distance_path, config_path = day_input_paths(args.data, args.day)
        output = args.output if args.output is not None else args.log.with_name("metrics.json")
        # The input files all live in the data directory, so this also protects them.
        if output.resolve() == args.data.resolve() or args.data.resolve() in output.resolve().parents:
            raise ValueError("report output must be outside the input data directory")
        if output.resolve() == args.log.resolve():
            raise ValueError("report output must not overwrite the log")
        with parcel_path.open(newline="", encoding="utf-8-sig") as stream:
            parcels = list(csv.DictReader(stream))
        with distance_path.open(newline="", encoding="utf-8-sig") as stream:
            distances = list(csv.DictReader(stream))
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        with args.log.open(encoding="utf-8") as stream:
            events = [json.loads(line) for line in stream if line.strip()]
        metrics = calculate_metrics(parcels, distances, config, events)
        report = json.dumps(metrics, indent=2, allow_nan=False) + "\n"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"Metrics report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
