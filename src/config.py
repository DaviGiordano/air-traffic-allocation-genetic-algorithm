"""
Configuration file for genetic algorithm hyperparameters and constants.
"""

# Hyperparameters
NUM_CHROMOSOMES = 100  # Population size (num_cromossomos)
MAX_ITERATIONS = 10000  # Maximum generations
INITIAL_MUTATION_RATE = (
    0.3  # Starting mutation probability (increased to explore more solutions)
)
AIRCRAFT_CAPACITY = 180  # Passengers per aircraft (typical for medium aircraft)

# Time constraints (all in minutes from midnight)
COOLDOWN_TIME = 60  # Cooldown after each flight
START_TIME = 360  # 6:00 AM
END_TIME = 1320  # 10:00 PM (22:00)
MAX_FLIGHT_TIME = 1080  # 18 hours total (including cooldowns, except last flight)

# Penalty weights for fitness function
UNSERVED_PENALTY = (
    40  # Weight for unserved passengers (increased to prioritize serving passengers)
)
STOP_PENALTY = 2  # Weight for number of stops
FLIGHT_PENALTY = 0.0  # Weight for total flights (set to 0 to not penalize flights)

# Evolution parameters
SELECTION_RATIO = 0.5  # Select best 50%
CROSSOVER_RATIO = 0.5  # Swap 50% of aircraft in crossover
ELITISM_SIZE = 1  # Number of best individuals to preserve

# Convergence
CONVERGENCE_THRESHOLD = 50.0  # Minimum improvement to continue (in fitness units)
CONVERGENCE_WINDOW = 200  # Check convergence over last N iterations (increased)
