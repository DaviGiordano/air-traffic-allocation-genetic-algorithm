# Genetic Algorithm for Brazilian Air Traffic Route Planning

This project implements a genetic algorithm using object-oriented design to optimize flight routes for 250 aircraft across 14 Brazilian airports, maximizing passenger demand satisfaction while minimizing unserved passengers, stops, and total flights.

## Project Structure

```
airalloc-ga3/
├── data/
│   ├── airports.csv          # Airport information (14 airports)
│   ├── demand_od.csv         # Origin-destination passenger demand
│   └── routes.csv            # Flight duration between airport pairs
├── src/
│   ├── models/               # Domain model classes
│   │   ├── aircraft_route.py    # AircraftRoute class
│   │   ├── chromosome.py        # Chromosome class
│   │   └── problem_data.py      # ProblemData class
│   ├── core/                 # Core algorithm classes
│   │   ├── route_scheduler.py      # Route scheduling and time calculations
│   │   ├── route_extractor.py      # Origin-destination pair extraction
│   │   ├── passenger_allocator.py  # Passenger allocation logic
│   │   ├── fitness_evaluator.py   # Fitness score calculation
│   │   ├── route_initializer.py   # Route initialization
│   │   ├── evolution_operator.py  # Crossover and mutation operators
│   │   └── genetic_algorithm.py   # Main GA orchestrator
│   ├── config.py             # Hyperparameters and constants
│   ├── data_loader.py        # CSV data loading functions
│   ├── timing.py             # Performance timing utilities
│   ├── visualization.py      # Result visualization
│   └── main.py               # Main entry point
├── requirements.txt          # Python dependencies
└── README.md
```

## Installation

1. Activate the virtual environment (if using .venv):
```bash
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the genetic algorithm:
```bash
python -m src.main
```

Or from the src directory:
```bash
cd src
python main.py
```

### Programmatic Usage

You can also use the classes programmatically:

```python
from src.data_loader import load_all_data
from src.models.problem_data import ProblemData
from src.core.genetic_algorithm import GeneticAlgorithm

# Load data
airport_codes, route_durations, demand_list = load_all_data("data")
problem_data = ProblemData(airport_codes, route_durations, demand_list)

# Create and run genetic algorithm
ga = GeneticAlgorithm(problem_data)
best_chromosome, stats = ga.run(verbose=True)

# Access results
print(f"Best fitness: {best_chromosome.get_fitness()}")
print(f"Unserved passengers: {stats['unserved_passengers']}")
print(f"Total flights: {stats['total_flights']}")
```

## Configuration

Edit `src/config.py` to adjust hyperparameters:

- `NUM_CHROMOSOMES`: Population size (default: 100)
- `MAX_ITERATIONS`: Maximum generations (default: 10000)
- `INITIAL_MUTATION_RATE`: Starting mutation probability (default: 0.3)
- `AIRCRAFT_CAPACITY`: Passengers per aircraft (default: 180)
- `UNSERVED_PENALTY`: Weight for unserved passengers (default: 40)
- `STOP_PENALTY`: Weight for number of stops (default: 2)
- `FLIGHT_PENALTY`: Weight for total flights (default: 0.0)
- `SELECTION_RATIO`: Fraction of population selected for reproduction (default: 0.5)
- `ELITISM_SIZE`: Number of best individuals preserved (default: 1)

## Architecture Overview

The codebase uses a clean object-oriented architecture with clear separation of concerns:

### Model Classes (`src/models/`)

- **`AircraftRoute`**: Represents a single aircraft route (sequence of airports)
  - Methods: `add_airport()`, `get_flight_legs()`, `get_length()`, `copy()`, `is_valid()`

- **`Chromosome`**: Represents a solution (collection of aircraft routes)
  - Methods: `add_route()`, `get_routes()`, `get_num_aircraft()`, `copy()`, `set_fitness()`, `get_fitness()`

- **`ProblemData`**: Holds all problem data (airports, routes, demand)
  - Methods: `get_airport_codes()`, `get_route_duration()`, `get_demand_list()`, `get_valid_next_airports()`

### Core Classes (`src/core/`)

- **`RouteScheduler`**: Handles time calculations and scheduling
  - Methods: `compute_schedule()`, `can_add_flight()`, `calculate_arrival_time()`, `add_cooldown_time()`

- **`RouteExtractor`**: Extracts origin-destination pairs from routes
  - Methods: `extract_od_pairs()`, `build_route_map()`, `update_capacity_in_map()`, `remove_aircraft_from_map()`

- **`PassengerAllocator`**: Handles passenger allocation to flights
  - Methods: `allocate_passengers()`, `find_best_route()`

- **`FitnessEvaluator`**: Calculates fitness scores
  - Methods: `evaluate()`, `_calculate_fitness_score()`, `_count_unique_flights()`

- **`RouteInitializer`**: Creates initial routes
  - Methods: `create_random_route()`, `initialize_chromosome()`, `_ensure_minimum_length()`

- **`EvolutionOperator`**: Handles crossover and mutation
  - Methods: `crossover()`, `mutate()`, `extend_route()`, `calculate_annealed_rate()`

- **`GeneticAlgorithm`**: Main GA orchestrator
  - Methods: `run()`, `_initialize_population()`, `_evaluate_population()`, `_evolve_generation()`, `_check_convergence()`

## Algorithm Overview

### Chromosome Representation
- A chromosome is a collection of 250 aircraft routes
- Each aircraft route is an ordered sequence of airport codes
- Routes respect time constraints (6:00 AM to 10:00 PM)
- Example: `Chromosome([AircraftRoute(['MA', 'BE', 'FO']), AircraftRoute(['SP', 'RJ', 'BH']), ...])`

### Fitness Function
The fitness score is minimized and calculated as:
```
score = UNSERVED_PENALTY * unserved_passengers 
      + STOP_PENALTY * total_stops 
      + FLIGHT_PENALTY * total_flights
```

Default weights:
- `UNSERVED_PENALTY = 40` (prioritizes serving passengers)
- `STOP_PENALTY = 2` (penalizes indirect routes)
- `FLIGHT_PENALTY = 0.0` (does not penalize flights)

### Evolution Process
1. **Initialization**: Generate random aircraft routes respecting time constraints
   - Routes have minimum 4 airports, maximum 15 airports
   - Routes fill available time window (6:00 AM to 10:00 PM)
2. **Evaluation**: Simulate passenger allocation and compute fitness
   - Allocates passengers to best available routes
   - Tracks unserved passengers, stops, and unique flights
3. **Selection**: Select best 50% of population (configurable via `SELECTION_RATIO`)
4. **Crossover**: Swap 50% of aircraft between parent chromosomes (configurable via `CROSSOVER_RATIO`)
5. **Mutation**: 
   - 60% chance to extend existing routes (encourages longer routes)
   - 40% chance to reinitialize routes (exploration)
   - Mutation rate anneals over time (starts at 0.3, decays to 0.05)
6. **Elitism**: Preserve best individual(s) (configurable via `ELITISM_SIZE`)
7. **Repeat** until convergence or max iterations

### Constraints
- Flights start at 6:00 AM (`START_TIME = 360`) and must complete by 10:00 PM (`END_TIME = 1320`)
- 60-minute cooldown after each flight (except the last) (`COOLDOWN_TIME = 60`)
- Routes must have minimum 4 airports, maximum 15 airports
- Aircraft capacity: 180 passengers per aircraft (configurable via `AIRCRAFT_CAPACITY`)
- Target: 250 aircraft × 4 flights average = 1000 total flights

## Data Format

### airports.csv
Columns: `code, city, state, airport_name, iata, icao, lat, lon`
- Contains 14 Brazilian airports

### routes.csv
Columns: `origin, dest, duration_min`
- Duration in minutes between airport pairs
- Defines valid flight connections

### demand_od.csv
Columns: `origin, dest, pax_daily`
- Daily passenger demand between origin and destination
- Used to evaluate route effectiveness

## Output

The algorithm outputs:
- Best chromosome (aircraft routes)
- Fitness statistics:
  - Unserved passengers
  - Total stops (weighted by passenger count)
  - Total flights operated (unique flight legs)
  - Detailed allocation information
- Visualization plots:
  - Statistics plot (`results/statistics.png`)
  - Route network plot (`results/routes_network.png`)
  - Aircraft routes plot (`results/aircraft_routes.png`)

## Code Quality

The codebase follows clean code principles:
- **Single Responsibility**: Each class has one clear purpose
- **Small Functions**: Methods are focused and do one thing well
- **Clear Naming**: Classes and methods have descriptive names
- **Encapsulation**: Related data and behavior are grouped together
- **Maintainability**: Code is easy to understand and modify

## Performance

The implementation includes timing utilities (`src/timing.py`) to track performance:
- Function execution times
- Call counts
- Performance summaries

Run with verbose mode to see timing statistics after execution.
