# IS115 G6 Project README

**Team 16:** Muhammad Amiruddin, Chua Jun Lin Jayden

## Overview

This project compares several dispatch policies for the IS115 dispatch simulator using the On-Time Delivery Rate (OTDR).

**OTDR (%) = (Parcels delivered within their preferred delivery windows ÷ total parcels) × 100**

## Project structure

- `solution/` — dispatch policies and helper functions
- `results/` — output logs and metric results
- `performance_monitor.py` — performance monitoring tool
- `run_experiments.py` — running all algorithms and giving a summary for comparison

## Run the experiments file

From the project root, run the simulation and calculate its OTDR:
```py run_experiments.py```


## Results summary
Metric: On-Time Delivery Rate (higher is better).

| Policy | On-Time Delivery Rate |
|---|---:|
| Baseline (First In First Out) | [27.41]% |
| Heuristic (Earliest Deadline First) | [17.99]% |
| Heuristic Feasible (Feasibility-Aware Earliest Deadline First )| [41.65]% |
| Heuristic (Greedy Nearest Neighbour)| [79.64]% |
| Heuristic Feasible (Local Search on NND)| [77.99]% |

## Results summary
Metric: On-Time Delivery Rate (higher is better).

| Policy | On-Time Delivery Rate |
|---|---:|
| Baseline (First In First Out) | [27.41]% |
| Heuristic (Earliest Deadline First) | [17.99]% |
| Heuristic Feasible (Feasibility-Aware Earliest Deadline First )| [41.65]% |
| Heuristic (Greedy Nearest Neighbour)| [79.64]% |
| Heuristic Feasible (Local Search on NND)| [77.99]% |

The main difference between the algorithms is how they balance simplicity with making better delivery decisions. FIFO and EDF are easier to implement, but they consider fewer factors when choosing which parcels to deliver. FA-EDF improves on this by checking whether parcels can arrive on time, while NND also considers the distance between delivery locations. Local Search goes a step further by trying to improve routes that have already been planned. However, improving one vehicle's route does not always mean better overall performance, as it may affect the vehicle's availability for later deliveries. 

Overall, this shows that a more complex algorithm does not necessarily lead to better results. We will compare how well each algorithm performs in Section 6 using the simulation results from all 20 days. 