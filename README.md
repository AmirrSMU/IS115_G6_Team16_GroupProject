# IS115 G6 Project README

**Team 16:** Muhammad Amiruddin, Chua Jun Lin Jayden

## NOTE
We did not use **helpers.py** for shared helper functions.

## Overview

This project compares several dispatch policies for the IS115 dispatch simulator using the On-Time Delivery Rate (OTDR).

**OTDR (%) = (Parcels delivered within their preferred delivery windows ÷ total parcels) × 100**

## Project structure

- `solution/` — dispatch policies and helper functions
- `results/` — output logs and metric results
- `performance_monitor.py` — performance monitoring tool
- `run_experiments.py` — running all algorithms and giving a summary for comparison

## Run the experiments file
- This experiments file was created with the aid of AI to help streamline and quicken to process of running and comparing the different algorithms created.
From the project root, run the simulation and calculate its OTDR:
```py run_experiments.py```

### Command to execute baseline.py
Run the simulator and calculate OTDR for all 20 days from the project root:

```powershell
1..20 | ForEach-Object {
    $dayId = "day_{0:D3}" -f $_
    $outputDir = "results/baseline.py/$dayId"

    py -m simulator --policy solution.policies.baseline --data data --day $dayId --output $outputDir
    py -m solution.performance_monitor --data data --day $dayId --log "$outputDir/log.txt"
}
```

Each day’s event log and `metrics.json` are saved in its corresponding folder under `results/heuristic_nnd/`.

### Command to execute heuristic_edf.py
Run the simulator and calculate OTDR for all 20 days from the project root:

```powershell
1..20 | ForEach-Object {
    $dayId = "day_{0:D3}" -f $_
    $outputDir = "results/heuristic_edf/$dayId"

    py -m simulator --policy solution.policies.heuristic_edf --data data --day $dayId --output $outputDir
    py -m solution.performance_monitor --data data --day $dayId --log "$outputDir/log.txt"
}
```

Each day’s event log and `metrics.json` are saved in its corresponding folder under `results/heuristic_nnd/`.

### Command to execute heuristic_feasible_edf.py
Run the simulator and calculate OTDR for all 20 days from the project root:

```powershell
1..20 | ForEach-Object {
    $dayId = "day_{0:D3}" -f $_
    $outputDir = "results/heuristic_feasible_edf/$dayId"

    py -m simulator --policy solution.policies.heuristic_feasible_edg --data data --day $dayId --output $outputDir
    py -m solution.performance_monitor --data data --day $dayId --log "$outputDir/log.txt"
}
```

Each day’s event log and `metrics.json` are saved in its corresponding folder under `results/heuristic_nnd/`.

### Command to execute heuristic_nnd.py
Run the simulator and calculate OTDR for all 20 days from the project root:

```powershell
1..20 | ForEach-Object {
    $dayId = "day_{0:D3}" -f $_
    $outputDir = "results/heuristic_nnd/$dayId"

    py -m simulator --policy solution.policies.heuristic_nnd --data data --day $dayId --output $outputDir
    py -m solution.performance_monitor --data data --day $dayId --log "$outputDir/log.txt"
}
```

Each day’s event log and `metrics.json` are saved in its corresponding folder under `results/heuristic_nnd/`.

### Command to execute localSearch_nnd.py
Run the simulator and calculate OTDR for all 20 days from the project root:

```powershell
1..20 | ForEach-Object {
    $dayId = "day_{0:D3}" -f $_
    $outputDir = "results/localSearch_nnd/$dayId"

    py -m simulator --policy solution.policies.localSearch_nnd --data data --day $dayId --output $outputDir
    py -m solution.performance_monitor --data data --day $dayId --log "$outputDir/log.txt"
}
```

Each day’s event log and `metrics.json` are saved in its corresponding folder under `results/heuristic_nnd/`.

## Results summary
Metric: On-Time Delivery Rate (higher is better).

| Policy | On-Time Delivery Rate |
|---|---:|
| Baseline (First In First Out) | 27.41% |
| Heuristic (Earliest Deadline First) | 17.99% |
| Heuristic Feasible (Feasibility-Aware Earliest Deadline First )| 41.65% |
| Heuristic (Greedy Nearest Neighbour)| 79.64% |
| Heuristic Feasible (Local Search on NND)| 77.99% |

The main difference between the algorithms is how they balance simplicity with making better delivery decisions. FIFO and EDF are easier to implement, but they consider fewer factors when choosing which parcels to deliver. FA-EDF improves on this by checking whether parcels can arrive on time, while NND also considers the distance between delivery locations. Local Search goes a step further by trying to improve routes that have already been planned. However, improving one vehicle's route does not always mean better overall performance, as it may affect the vehicle's availability for later deliveries. 

Overall, this shows that a more complex algorithm does not necessarily lead to better results. We will compare how well each algorithm performs in Section 6 using the simulation results from all 20 days. 