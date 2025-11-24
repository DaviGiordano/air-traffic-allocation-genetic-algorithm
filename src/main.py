"""Main entry point for the genetic algorithm."""

from src.data_loader import load_all_data
from src.models.problem_data import ProblemData
from src.core.genetic_algorithm import GeneticAlgorithm
from src.visualization import visualize_results


def main():
    """Main entry point."""
    print("Loading data...")
    airport_codes, route_durations, demand_list = load_all_data("data")

    print(f"Loaded {len(airport_codes)} airports")
    print(f"Loaded {len(route_durations)} routes")
    print(f"Loaded {len(demand_list)} demand pairs")

    # Create problem data
    problem_data = ProblemData(airport_codes, route_durations, demand_list)

    print("\nRunning genetic algorithm...")
    ga = GeneticAlgorithm(problem_data)
    best_chromosome, stats = ga.run(verbose=True)

    print("\nAlgorithm completed!")

    # Visualize results
    if best_chromosome and stats:
        print("\nGenerating visualizations...")
        # Convert chromosome to list format for visualization
        chromosome_list = [route.get_airports() for route in best_chromosome.get_routes()]
        visualize_results(chromosome_list, stats, airport_codes, save_dir="results")

    return best_chromosome, stats


if __name__ == "__main__":
    main()
