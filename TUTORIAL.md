# Tutorial: Understanding and Navigating the Air Traffic Allocation Genetic Algorithm Repository

## Table of Contents
1. [Overview](#overview)
2. [Repository Structure](#repository-structure)
3. [Getting Started](#getting-started)
4. [Understanding the Problem](#understanding-the-problem)
5. [Code Architecture](#code-architecture)
6. [Data Flow](#data-flow)
7. [Key Components Deep Dive](#key-components-deep-dive)
8. [Running the Algorithm](#running-the-algorithm)
9. [Understanding Results](#understanding-results)
10. [Customization Guide](#customization-guide)
11. [Common Tasks](#common-tasks)

---

## Overview

This repository implements a **Genetic Algorithm (GA)** to solve an air traffic route planning problem for Brazilian airports. The algorithm optimizes the allocation of 250 aircraft across 14 airports to maximize passenger demand satisfaction while minimizing unserved passengers and flight stops.

### Key Concepts
- **Chromosome**: A complete solution representing 250 aircraft routes
- **Gene**: A single aircraft route (sequence of airports)
- **Fitness**: A score measuring solution quality (lower is better)
- **Evolution**: Process of improving solutions through selection, crossover, and mutation

---

## Repository Structure

```
air-traffic-allocation-genetic-algorithm/
├── data/                          # Input data files
│   ├── airports.csv              # 14 Brazilian airports
│   ├── routes.csv                # Flight durations between airports
│   └── demand_od.csv             # Origin-destination passenger demand
│
├── src/                          # Source code
│   ├── models/                   # Domain model classes
│   │   ├── aircraft_route.py     # Single aircraft route representation
│   │   ├── chromosome.py         # Complete solution (250 routes)
│   │   └── problem_data.py       # Problem data container
│   │
│   ├── core/                     # Core algorithm components
│   │   ├── genetic_algorithm.py  # Main GA orchestrator
│   │   ├── route_initializer.py  # Initial population generation
│   │   ├── fitness_evaluator.py # Fitness calculation
│   │   ├── passenger_allocator.py # Passenger allocation simulation
│   │   ├── route_extractor.py    # Extract OD pairs from routes
│   │   ├── route_scheduler.py    # Time scheduling logic
│   │   └── evolution_operator.py # Crossover and mutation
│   │
│   ├── config.py                 # Hyperparameters and constants
│   ├── data_loader.py            # CSV file loading
│   ├── visualization.py          # Result plotting
│   ├── timing.py                 # Performance profiling
│   └── main.py                   # Entry point
│
├── results/                      # Output directory
│   ├── best_chromosome.pkl      # Best solution found
│   ├── stats.pkl                # Statistics dictionary
│   ├── genetic_algorithm.pkl    # GA state
│   ├── statistics.png           # Statistics dashboard
│   ├── routes_network.png       # Network visualization
│   └── aircraft_routes.png      # Individual route plots
│
├── notebooks/                    # Jupyter notebooks
│   └── 1. Results.ipynb         # Analysis notebook
│
├── run.py                        # Simple execution script
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Poetry configuration
├── README.md                    # Project overview
└── DOCUMENTACAO.md              # Detailed documentation (Portuguese)
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Installation

1. **Activate virtual environment** (if using `.venv`):
```bash
source .venv/bin/activate
```

2. **Install dependencies**:
```bash
uv pip install -r requirements.txt
```

Or using Poetry:
```bash
poetry install
```

### Quick Run

Execute the algorithm:
```bash
python run.py
```

Or:
```bash
python -m src.main
```

---

## Understanding the Problem

### Problem Statement

**Goal**: Allocate 250 aircraft to serve ~180,000 daily passengers across 14 Brazilian airports, maximizing demand satisfaction while minimizing:
- Unserved passengers
- Number of flight stops (prefer direct flights)
- Total flights operated

### Constraints

1. **Time Window**: Operations between 06:00 and 22:00 (16 hours)
2. **Cooldown**: 60 minutes wait after each flight (except last)
3. **Maximum Flight Time**: 18 hours total including cooldowns
4. **Aircraft Capacity**: 200 passengers per aircraft
5. **Departure Times**: Must be at full hours (06:00, 07:00, etc.)
6. **Minimum Connections**: 60 minutes between connections
7. **Route Validity**: Only routes defined in `routes.csv` are valid

### Data Files

#### `data/airports.csv`
Contains 14 Brazilian airports with codes like:
- `MA` (Manaus)
- `SP` (São Paulo)
- `RJ` (Rio de Janeiro)
- etc.

#### `data/routes.csv`
Defines valid flight connections:
```csv
origin,dest,duration_min
MA,BE,120
BE,FO,120
...
```

#### `data/demand_od.csv`
Passenger demand between origin-destination pairs:
```csv
origin,dest,pax_daily
MA,BE,350
FO,BH,600
...
```

---

## Code Architecture

### Design Philosophy

The codebase follows **object-oriented design** with clear separation of concerns:

1. **Models** (`src/models/`): Data structures representing domain concepts
2. **Core** (`src/core/`): Algorithm logic and operations
3. **Utilities** (`src/`): Supporting functions (data loading, visualization, timing)

### Class Hierarchy

```
ProblemData (holds airports, routes, demand)
    │
    ├── RouteInitializer (creates initial routes)
    │
    ├── GeneticAlgorithm (main orchestrator)
    │   ├── FitnessEvaluator (evaluates solutions)
    │   │   └── PassengerAllocator (simulates allocation)
    │   │       └── RouteExtractor (extracts OD pairs)
    │   │           └── RouteScheduler (calculates times)
    │   │
    │   └── EvolutionOperator (crossover & mutation)
    │
    └── Chromosome (solution)
        └── AircraftRoute[] (250 routes)
```

---

## Data Flow

### Execution Flow

```
1. Load Data (data_loader.py)
   ├── airports.csv → airport_codes[]
   ├── routes.csv → route_durations{(origin, dest): duration}
   └── demand_od.csv → demand_list[(origin, dest, passengers)]

2. Create ProblemData
   └── Wraps all data in ProblemData object

3. Initialize GeneticAlgorithm
   ├── RouteInitializer
   ├── FitnessEvaluator
   │   └── PassengerAllocator
   └── EvolutionOperator

4. Run GA Loop (genetic_algorithm.py)
   ├── Initialize Population (100 chromosomes)
   │   └── Each chromosome = 250 random routes
   │
   ├── Evaluate Population
   │   ├── For each chromosome:
   │   │   ├── Extract OD pairs from routes
   │   │   ├── Allocate passengers to routes
   │   │   └── Calculate fitness score
   │   └── Store fitness in chromosome
   │
   ├── Evolution (repeat until convergence)
   │   ├── Select Parents (best 50%)
   │   ├── Crossover (swap 50% of routes)
   │   ├── Mutate (extend or reinitialize routes)
   │   ├── Evaluate Offspring
   │   ├── Elitism (preserve best)
   │   └── Update Population
   │
   └── Return Best Solution

5. Visualize Results
   └── Generate plots and save files
```

### Fitness Evaluation Flow

```
Chromosome (250 routes)
    │
    ├── RouteExtractor.extract_od_pairs()
    │   └── For each route, extract all possible OD pairs
    │       └── MA→BE→FO extracts: MA→BE, MA→FO, BE→FO
    │
    ├── RouteExtractor.build_route_map()
    │   └── Map each OD pair → list of available routes
    │       └── Sorted by: stops (asc), time (asc)
    │
    ├── PassengerAllocator.allocate_passengers()
    │   ├── Initialize leg capacities (200 per leg)
    │   ├── Shuffle demand list
    │   ├── For each demand:
    │   │   ├── Find best route (first in sorted list)
    │   │   ├── Check capacity
    │   │   ├── Allocate passengers (can be partial)
    │   │   └── Update capacities
    │   └── Return allocations + unmet demands
    │
    └── FitnessEvaluator._calculate_fitness_score()
        └── fitness = 100×unserved + 2×stops + 0×flights
```

---

## Key Components Deep Dive

### 1. Models (`src/models/`)

#### `AircraftRoute` (`aircraft_route.py`)
Represents a single aircraft's route as a sequence of airports.

**Key Methods**:
- `get_airports()`: Returns list of airport codes
- `get_flight_legs()`: Returns list of (origin, dest) tuples
- `get_length()`: Number of airports in route
- `is_valid()`: Checks if all legs exist in route_durations

**Example**:
```python
route = AircraftRoute(['MA', 'BE', 'FO', 'NA'])
# Represents flights: MA→BE, BE→FO, FO→NA
```

#### `Chromosome` (`chromosome.py`)
Represents a complete solution: collection of 250 aircraft routes.

**Key Methods**:
- `get_routes()`: Returns list of AircraftRoute objects
- `get_num_aircraft()`: Returns 250
- `set_fitness(fitness)`: Stores fitness score
- `get_fitness()`: Retrieves fitness score
- `copy()`: Creates deep copy

**Example**:
```python
chromosome = Chromosome([route1, route2, ..., route250])
chromosome.set_fitness(1250.5)
```

#### `ProblemData` (`problem_data.py`)
Container for all problem data (airports, routes, demand).

**Key Methods**:
- `get_airport_codes()`: List of airport codes
- `get_route_duration(origin, dest)`: Duration in minutes
- `get_demand_list()`: List of (origin, dest, passengers)
- `get_valid_next_airports(airport)`: Reachable airports

---

### 2. Core Components (`src/core/`)

#### `RouteScheduler` (`route_scheduler.py`)
Handles time calculations and scheduling.

**Key Methods**:
- `compute_schedule(route, route_durations)`: Calculates departure/arrival times
  - Returns: `[(departure_time, airport, arrival_time), ...]`
- `can_add_flight(...)`: Checks if flight fits in time window

**Example**:
```python
route = AircraftRoute(['MA', 'BE', 'FO'])
schedule = RouteScheduler.compute_schedule(route, route_durations)
# Returns: [(360, 'MA', 480), (540, 'BE', 660), (840, 'FO', 900)]
# Times in minutes from midnight (360 = 06:00)
```

#### `RouteExtractor` (`route_extractor.py`)
Extracts all possible origin-destination pairs from routes.

**Key Methods**:
- `extract_od_pairs(route, route_durations)`: Extracts all OD pairs
  - For route `['MA', 'BE', 'FO']`:
    - Extracts: MA→BE (direct), MA→FO (1 stop), BE→FO (direct)
- `build_route_map(chromosome, problem_data, leg_capacities)`: Builds route lookup
  - Returns: `{(origin, dest): [(aircraft_id, stops, time, capacity, start_idx, end_idx), ...]}`
- `initialize_leg_capacities(chromosome, capacity)`: Sets capacity per leg

**Example**:
```python
route_map = RouteExtractor.build_route_map(chromosome, problem_data, capacities)
# route_map[('MA', 'FO')] = [
#     (0, 1, 240, 180, 0, 2),  # Aircraft 0, 1 stop, 240 min, 180 capacity
#     (5, 0, 120, 200, 1, 2),  # Aircraft 5, direct, 120 min, 200 capacity
# ]
```

#### `PassengerAllocator` (`passenger_allocator.py`)
Simulates passenger allocation to flights.

**Key Methods**:
- `allocate_passengers(chromosome)`: Main allocation logic
  - Returns: `(leg_capacities, allocations, unmet_demands)`

**Algorithm**:
1. Initialize capacities (200 passengers per leg)
2. Build route map (all available routes)
3. Shuffle demand list
4. For each demand:
   - Find best route (first in sorted list)
   - Check segment capacity
   - Allocate passengers (can be partial)
   - Update capacities
   - If partial, re-queue remaining demand

**Example Output**:
```python
allocations = [
    ('MA', 'BE', 180, 0, 0),  # 180 passengers, aircraft 0, 0 stops
    ('MA', 'FO', 150, 0, 1),  # 150 passengers, aircraft 0, 1 stop
]
unmet_demands = [
    ('SP', 'PA', 250),  # 250 passengers not served
]
```

#### `FitnessEvaluator` (`fitness_evaluator.py`)
Calculates fitness score for a chromosome.

**Key Methods**:
- `evaluate(chromosome)`: Main evaluation
  - Returns: `(fitness_score, statistics_dict)`

**Fitness Formula**:
```python
fitness = UNSERVED_PENALTY × unserved_passengers
        + STOP_PENALTY × total_stops
        + FLIGHT_PENALTY × total_flights

# Default weights:
# UNSERVED_PENALTY = 100
# STOP_PENALTY = 2
# FLIGHT_PENALTY = 0.0
```

**Statistics Dictionary**:
```python
stats = {
    'unserved_passengers': 1250,
    'total_stops': 3500,
    'total_flights': 980,
    'allocations': [...],
    'unmet_demands': [...],
}
```

#### `RouteInitializer` (`route_initializer.py`)
Creates initial random routes.

**Key Methods**:
- `create_random_route()`: Creates one random route
  - Starts at random airport at 06:00
  - Adds airports randomly until time limit
  - Ensures minimum 4 airports
- `initialize_chromosome()`: Creates chromosome with 250 routes

**Algorithm**:
1. Start at random airport, time = 360 (06:00)
2. While time < 1320 (22:00) and route length < 15:
   - Select random valid next airport
   - Calculate flight duration
   - If arrival <= 22:00: add airport, add cooldown
   - Else: stop
3. Ensure minimum 4 airports

#### `EvolutionOperator` (`evolution_operator.py`)
Handles crossover and mutation.

**Key Methods**:
- `crossover(parent1, parent2)`: Swaps 50% of routes between parents
- `mutate(chromosome, mutation_rate)`: Mutates routes
  - 60% chance: extend route
  - 40% chance: reinitialize route
- `calculate_annealed_rate(initial_rate, generation, max_generations)`: Decays mutation rate

**Crossover Example**:
```python
parent1 = Chromosome([A1, A2, A3, ..., A250])
parent2 = Chromosome([B1, B2, B3, ..., B250])

# Swap 50% randomly selected routes
child1 = Chromosome([A1, B2, A3, B4, ..., B250])
child2 = Chromosome([B1, A2, B3, A4, ..., A250])
```

**Mutation Rate Annealing**:
```python
mutation_rate(t) = max(0.05, initial_rate × 0.5^(2×t/T))
# Starts at 0.3, decays to 0.05 over generations
```

#### `GeneticAlgorithm` (`genetic_algorithm.py`)
Main orchestrator for the genetic algorithm.

**Key Methods**:
- `run(verbose=True)`: Main execution loop
- `_initialize_population()`: Creates initial population
- `_evaluate_population()`: Evaluates all chromosomes
- `_select_parents()`: Selects best 50%
- `_evolve_generation()`: One generation of evolution
- `_check_convergence()`: Checks if converged

**Main Loop**:
```python
1. Initialize population (100 chromosomes)
2. Evaluate population
3. For each generation:
   a. Calculate mutation rate (annealed)
   b. Select parents (best 50%)
   c. Create offspring (crossover + mutation)
   d. Evaluate offspring
   e. Apply elitism
   f. Update population
   g. Check convergence
4. Return best solution
```

---

## Running the Algorithm

### Basic Execution

```bash
python run.py
```

This will:
1. Load data from `data/` directory
2. Run genetic algorithm
3. Generate visualizations
4. Save results to `results/` directory

### Programmatic Usage

```python
from src.data_loader import load_all_data
from src.models.problem_data import ProblemData
from src.core.genetic_algorithm import GeneticAlgorithm

# Load data
airport_codes, route_durations, demand_list = load_all_data("data")
problem_data = ProblemData(airport_codes, route_durations, demand_list)

# Create and run GA
ga = GeneticAlgorithm(problem_data)
best_chromosome, stats = ga.run(verbose=True)

# Access results
print(f"Fitness: {best_chromosome.get_fitness()}")
print(f"Unserved passengers: {stats['unserved_passengers']}")
print(f"Total stops: {stats['total_stops']}")
```

### Configuration

Edit `src/config.py` to adjust hyperparameters:

```python
NUM_CHROMOSOMES = 100          # Population size
MAX_ITERATIONS = 100           # Max generations
INITIAL_MUTATION_RATE = 0.3    # Starting mutation rate
AIRCRAFT_CAPACITY = 200        # Passengers per aircraft
UNSERVED_PENALTY = 100         # Weight for unserved passengers
STOP_PENALTY = 2               # Weight for stops
SELECTION_RATIO = 0.5          # Fraction selected as parents
CROSSOVER_RATIO = 0.5          # Fraction swapped in crossover
ELITISM_SIZE = 1               # Number of best preserved
NUM_WORKERS = -1               # Parallel workers
```

---

## Understanding Results

### Output Files

#### `results/best_chromosome.pkl`
Serialized best chromosome found. Load with:
```python
import pandas as pd
best_chromosome = pd.read_pickle("results/best_chromosome.pkl")
routes = best_chromosome.get_routes()
```

#### `results/stats.pkl`
Statistics dictionary. Contains:
- `unserved_passengers`: Number of passengers not served
- `total_stops`: Total stops (weighted by passengers)
- `total_flights`: Number of unique flight legs
- `allocations`: List of allocations `[(origin, dest, passengers, aircraft_id, stops), ...]`
- `unmet_demands`: List of unmet demands `[(origin, dest, passengers), ...]`

#### `results/genetic_algorithm.pkl`
Complete GA state (for resuming runs).

### Visualizations

#### `results/statistics.png`
Dashboard showing:
- Top 10 OD pairs by passengers allocated
- Top 50 aircraft utilization
- Key metrics (unserved passengers, stops, flights, fitness)
- Service rate pie chart

#### `results/routes_network.png`
Network visualization:
- Nodes = airports
- Edges = routes used
- Edge thickness = usage intensity
- Gray edges = unused routes

#### `results/aircraft_routes.png`
Individual routes for top 20 most utilized aircraft:
- Shows route path
- Highlights passenger allocations
- Displays utilization

### Interpreting Results

**Good Solution Indicators**:
- Low fitness score (< 5000)
- Low unserved passengers (< 1000)
- Low average stops per passenger (< 0.5)
- High aircraft utilization (most aircraft used)

**Poor Solution Indicators**:
- High fitness score (> 20000)
- Many unserved passengers (> 10000)
- High average stops (> 1.0)
- Low aircraft utilization

---

## Customization Guide

### Changing Problem Size

To use different number of aircraft:

1. Modify `RouteInitializer.initialize_chromosome()`:
```python
# Change from 250 to N aircraft
for _ in range(N):  # Instead of 250
    route = self.create_random_route()
    chromosome.add_route(route)
```

2. Update `ProblemData` initialization if needed.

### Modifying Fitness Function

Edit `FitnessEvaluator._calculate_fitness_score()`:

```python
def _calculate_fitness_score(self, stats):
    fitness = (
        UNSERVED_PENALTY * stats['unserved_passengers']
        + STOP_PENALTY * stats['total_stops']
        + FLIGHT_PENALTY * stats['total_flights']
        + YOUR_NEW_PENALTY * stats['your_metric']  # Add new term
    )
    return fitness
```

### Adding New Constraints

1. **Time Constraints**: Modify `RouteScheduler.compute_schedule()`
2. **Capacity Constraints**: Modify `PassengerAllocator.allocate_passengers()`
3. **Route Constraints**: Modify `RouteInitializer.create_random_route()`

### Custom Mutation Strategy

Edit `EvolutionOperator.mutate()`:

```python
def mutate(self, chromosome, mutation_rate):
    # Add your custom mutation logic
    if random.random() < 0.3:
        # Your custom mutation
        pass
    # ... existing mutations
```

---

## Common Tasks

### Task 1: Analyze a Specific Solution

```python
import pandas as pd

# Load best chromosome
chromosome = pd.read_pickle("results/best_chromosome.pkl")
stats = pd.read_pickle("results/stats.pkl")

# Get routes
routes = chromosome.get_routes()

# Analyze specific aircraft
aircraft_id = 0
route = routes[aircraft_id]
print(f"Aircraft {aircraft_id}: {route.get_airports()}")

# Find allocations for this aircraft
aircraft_allocations = [
    alloc for alloc in stats['allocations']
    if alloc[3] == aircraft_id  # aircraft_id is index 3
]
print(f"Allocations: {aircraft_allocations}")
```

### Task 2: Check Unmet Demand

```python
import pandas as pd

stats = pd.read_pickle("results/stats.pkl")
unmet = stats['unmet_demands']

# Group by origin
from collections import defaultdict
by_origin = defaultdict(int)
for origin, dest, pax in unmet:
    by_origin[origin] += pax

print("Unmet demand by origin:")
for origin, total in sorted(by_origin.items(), key=lambda x: -x[1]):
    print(f"{origin}: {total} passengers")
```

### Task 3: Calculate Route Utilization

```python
import pandas as pd
from collections import defaultdict

stats = pd.read_pickle("results/stats.pkl")
allocations = stats['allocations']

# Count passengers per route segment
route_usage = defaultdict(int)
for origin, dest, passengers, aircraft_id, stops in allocations:
    route_usage[(origin, dest)] += passengers

# Sort by usage
top_routes = sorted(route_usage.items(), key=lambda x: -x[1])[:10]
print("Top 10 routes by passengers:")
for (origin, dest), passengers in top_routes:
    print(f"{origin}→{dest}: {passengers} passengers")
```

### Task 4: Modify Initialization Strategy

Edit `RouteInitializer.create_random_route()`:

```python
def create_random_route(self):
    # Your custom initialization logic
    # Example: Start from high-demand airports
    high_demand_airports = ['SP', 'RJ', 'BH']
    start_airport = random.choice(high_demand_airports)
    # ... rest of initialization
```

### Task 5: Add Custom Visualization

Create new function in `visualization.py`:

```python
def plot_custom_analysis(stats, save_path="results/custom.png"):
    # Your visualization code
    import matplotlib.pyplot as plt
    # ... plotting code
    plt.savefig(save_path)
```

---

## Troubleshooting

### Issue: Algorithm Not Converging

**Solutions**:
1. Increase `MAX_ITERATIONS` in `config.py`
2. Increase `NUM_CHROMOSOMES` (larger population)
3. Adjust `INITIAL_MUTATION_RATE` (try 0.2-0.4)
4. Check convergence threshold: `CONVERGENCE_THRESHOLD`

### Issue: Too Many Unserved Passengers

**Solutions**:
1. Increase `AIRCRAFT_CAPACITY` if realistic
2. Increase number of aircraft (modify initialization)
3. Adjust `UNSERVED_PENALTY` to prioritize serving passengers
4. Check if demand is realistic (total demand vs capacity)

### Issue: Slow Execution

**Solutions**:
1. Enable multiprocessing: Set `NUM_WORKERS > 1` in `config.py`
2. Reduce `NUM_CHROMOSOMES` (smaller population)
3. Reduce `MAX_ITERATIONS` (fewer generations)
4. Use `verbose=False` to disable progress bars

### Issue: Invalid Routes Generated

**Check**:
1. Verify `routes.csv` contains all necessary connections
2. Check `RouteInitializer.create_random_route()` logic
3. Ensure `RouteScheduler` respects time constraints
4. Validate routes with `AircraftRoute.is_valid()`

---

## Next Steps

1. **Read the Code**: Start with `src/main.py` and follow the execution flow
2. **Experiment**: Modify hyperparameters in `config.py`
3. **Analyze Results**: Use Jupyter notebook in `notebooks/`
4. **Extend**: Add new features (constraints, operators, visualizations)
5. **Document**: Update `DOCUMENTACAO.md` with your changes

---

## Additional Resources

- **Detailed Documentation**: See `DOCUMENTACAO.md` (Portuguese)
- **Code Comments**: All modules have docstrings
- **Type Hints**: Code uses type hints for clarity
- **Jupyter Notebook**: `notebooks/1. Results.ipynb` for analysis

---

## Summary

This repository implements a genetic algorithm for air traffic route planning with:

- **Clean Architecture**: Separated models, core logic, and utilities
- **Modular Design**: Each component has a single responsibility
- **Extensible**: Easy to modify and extend
- **Well-Documented**: Comprehensive docstrings and documentation

**Key Files to Understand**:
1. `src/main.py` - Entry point
2. `src/core/genetic_algorithm.py` - Main GA loop
3. `src/core/fitness_evaluator.py` - Fitness calculation
4. `src/core/passenger_allocator.py` - Allocation logic
5. `src/config.py` - Hyperparameters

**Key Concepts**:
- Chromosome = Solution (250 routes)
- Gene = Single route
- Fitness = Quality score (lower is better)
- Evolution = Selection + Crossover + Mutation

Happy exploring! 🚀

