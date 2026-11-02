
import csv
import json
import subprocess
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent

# Add your algorithms here.
# Only include policies that already exist.
ALGORITHMS = [
    "baseline",
    "heuristic_edf",
    "heuristic_feasible_edf",
    # "heuristic_nn",
    # "heuristic_hybrid",
]

DAYS = range(1, 21)


def run_command(command):
    """Execute a command and stop if it fails."""
    subprocess.run(
        command,
        cwd=ROOT,
        check=True
    )


def run_experiments():
    results = []

    for algorithm in ALGORITHMS:

        policy_file = (
            ROOT / "solution" / "policies"
            / f"{algorithm}.py"
        )

        if not policy_file.is_file():
            raise FileNotFoundError(
                f"Algorithm file missing: {policy_file}"
            )

        for number in DAYS:
            day = f"day_{number:03d}"
            output = ROOT / "results" / algorithm / day
            output.mkdir(parents=True, exist_ok=True)

            print(
                f"\nRunning {algorithm} on {day}",
                flush=True
            )

            # Step 1: Run simulator
            run_command([
                sys.executable,
                "-m", "simulator",
                "--policy", f"solution.policies.{algorithm}",
                "--data", "data",
                "--day", day,
                "--output", str(output)
            ])

            # Step 2: Run performance monitor
            log_file = output / "log.txt"

            run_command([
                sys.executable,
                "-m", "solution.performance_monitor",
                "--data", "data",
                "--day", day,
                "--log", str(log_file)
            ])

            # Step 3: Read metrics
            metrics_file = output / "metrics.json"

            with open(metrics_file, encoding="utf-8") as f:
                metrics = json.load(f)

            results.append({
                "algorithm": algorithm,
                "day": day,
                "total_parcels": metrics["total_parcels"],
                "delivered_parcels": metrics["delivered_parcels"],
                "on_time_deliveries": metrics["on_time_deliveries"],
                "otdr_percent": metrics["otdr_percent"]
            })

            print(
                f"OTDR: {metrics['otdr_percent']:.2f}%",
                flush=True
            )

    # Step 4: Save comparison spreadsheet
    summary_path = ROOT / "results" / "summary.csv"

    with open(
        summary_path, "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "algorithm",
                "day",
                "total_parcels",
                "delivered_parcels",
                "on_time_deliveries",
                "otdr_percent"
            ]
        )
        writer.writeheader()
        writer.writerows(results)

    # Step 5: Calculate averages for each algorithm
    print("\n===== FINAL SUMMARY =====")

    for algorithm in ALGORITHMS:
        rows = [
            r for r in results
            if r["algorithm"] == algorithm
        ]

        average_otdr = (
            sum(r["otdr_percent"] for r in rows)
            / len(rows)
        )

        overall_otdr = (
            sum(r["on_time_deliveries"] for r in rows)
            / sum(r["total_parcels"] for r in rows)
            * 100
        )

        print(
            f"{algorithm}: "
            f"Average daily OTDR = {average_otdr:.2f}% | "
            f"Overall OTDR = {overall_otdr:.2f}%"
        )

    print(f"\nResults saved to: {summary_path}")


if __name__ == "__main__":
    run_experiments()
