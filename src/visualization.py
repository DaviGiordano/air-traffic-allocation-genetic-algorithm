"""
Visualization module for genetic algorithm results.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np


def plot_statistics(stats: Dict, save_path: str = None):
    """
    Plot statistics from simulation results.

    Args:
        stats: Statistics dictionary from simulate_chromosome
        save_path: Optional path to save the figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Genetic Algorithm Results - Statistics", fontsize=16, fontweight="bold")

    # 1. Allocation breakdown
    allocations = stats.get("allocations", [])
    if allocations:
        od_pairs = defaultdict(int)
        for origin, dest, pax, _, _ in allocations:
            od_pairs[f"{origin}→{dest}"] += pax

        # Get top 10 OD pairs
        top_od = sorted(od_pairs.items(), key=lambda x: x[1], reverse=True)[:10]
        od_names = [item[0] for item in top_od]
        od_counts = [item[1] for item in top_od]

        axes[0, 0].barh(od_names, od_counts)
        axes[0, 0].set_xlabel("Passengers Allocated")
        axes[0, 0].set_title("Top 10 Origin-Destination Pairs")
        axes[0, 0].grid(axis="x", alpha=0.3)
    else:
        axes[0, 0].text(
            0.5,
            0.5,
            "No Allocations",
            ha="center",
            va="center",
            transform=axes[0, 0].transAxes,
        )
        axes[0, 0].set_title("Top 10 Origin-Destination Pairs")

    # 2. Aircraft utilization
    if allocations:
        aircraft_usage = defaultdict(int)
        for _, _, pax, aircraft_id, _ in allocations:
            aircraft_usage[aircraft_id] += pax

        aircraft_ids = sorted(aircraft_usage.keys())
        usage_values = [aircraft_usage[aid] for aid in aircraft_ids]

        axes[0, 1].bar(aircraft_ids[:50], usage_values[:50], alpha=0.7)  # Show first 50
        axes[0, 1].set_xlabel("Aircraft ID")
        axes[0, 1].set_ylabel("Passengers Allocated")
        axes[0, 1].set_title(f"Aircraft Utilization (Top 50 of {len(aircraft_ids)})")
        axes[0, 1].grid(axis="y", alpha=0.3)
    else:
        axes[0, 1].text(
            0.5,
            0.5,
            "No Allocations",
            ha="center",
            va="center",
            transform=axes[0, 1].transAxes,
        )
        axes[0, 1].set_title("Aircraft Utilization")

    # 3. Summary metrics
    metrics = {
        "Unserved Passengers": stats.get("unserved_passengers", 0),
        "Total Stops": stats.get("total_stops", 0),
        "Total Flights": stats.get("total_flights", 0),
        "Fitness Score": stats.get("fitness_score", 0),
    }

    metric_names = list(metrics.keys())
    metric_values = list(metrics.values())

    bars = axes[1, 0].bar(metric_names, metric_values, color=["red", "orange", "blue", "green"])
    axes[1, 0].set_ylabel("Value")
    axes[1, 0].set_title("Key Metrics")
    axes[1, 0].tick_params(axis="x", rotation=45)
    axes[1, 0].grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bar, value in zip(bars, metric_values):
        height = bar.get_height()
        axes[1, 0].text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{value:,.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # 4. Service rate pie chart
    if allocations:
        total_served = sum(pax for _, _, pax, _, _ in allocations)
        total_unserved = stats.get("unserved_passengers", 0)
        total_demand = total_served + total_unserved

        if total_demand > 0:
            sizes = [total_served, total_unserved]
            labels = [
                f"Served\n{total_served:,} ({total_served/total_demand*100:.1f}%)",
                f"Unserved\n{total_unserved:,} ({total_unserved/total_demand*100:.1f}%)",
            ]
            colors = ["#2ecc71", "#e74c3c"]

            axes[1, 1].pie(sizes, labels=labels, colors=colors, autopct="", startangle=90)
            axes[1, 1].set_title("Passenger Service Rate")
        else:
            axes[1, 1].text(
                0.5,
                0.5,
                "No Demand Data",
                ha="center",
                va="center",
                transform=axes[1, 1].transAxes,
            )
            axes[1, 1].set_title("Passenger Service Rate")
    else:
        axes[1, 1].text(
            0.5,
            0.5,
            "No Allocations",
            ha="center",
            va="center",
            transform=axes[1, 1].transAxes,
        )
        axes[1, 1].set_title("Passenger Service Rate")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Statistics plot saved to {save_path}")
    else:
        plt.show()


def plot_routes(
    chromosome: List[List[str]],
    stats: Dict,
    airport_codes: List[str],
    save_path: str = None,
    max_routes: int = 50,
):
    """
    Plot aircraft routes on a network graph.

    Args:
        chromosome: Best chromosome (list of aircraft routes)
        stats: Statistics dictionary
        airport_codes: List of airport codes
        save_path: Optional path to save the figure
        max_routes: Maximum number of routes to display
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.suptitle("Aircraft Routes Network", fontsize=16, fontweight="bold")

    # Count route usage
    route_usage = defaultdict(int)
    if stats.get("allocations"):
        for origin, dest, pax, aircraft_id, stops in stats["allocations"]:
            route = chromosome[aircraft_id]
            try:
                origin_idx = route.index(origin)
                dest_idx = route.index(dest)
                if dest_idx > origin_idx:
                    for i in range(origin_idx, dest_idx):
                        leg = (route[i], route[i + 1])
                        route_usage[leg] += pax
            except ValueError:
                pass

    # Create position map for airports (circular layout)
    n_airports = len(airport_codes)
    angles = np.linspace(0, 2 * np.pi, n_airports, endpoint=False)
    radius = 1.0
    positions = {}
    for i, code in enumerate(airport_codes):
        x = radius * np.cos(angles[i])
        y = radius * np.sin(angles[i])
        positions[code] = (x, y)

    # Draw routes (only show routes with allocations)
    if route_usage:
        sorted_routes = sorted(route_usage.items(), key=lambda x: x[1], reverse=True)
        max_usage = max(usage for _, usage in sorted_routes)

        for (origin, dest), usage in sorted_routes[:max_routes]:
            x1, y1 = positions.get(origin, (0, 0))
            x2, y2 = positions.get(dest, (0, 0))

            # Line width proportional to usage
            linewidth = 1 + 3 * (usage / max_usage) if max_usage > 0 else 1
            alpha = 0.3 + 0.5 * (usage / max_usage) if max_usage > 0 else 0.3

            ax.plot([x1, x2], [y1, y2], "b-", alpha=alpha, linewidth=linewidth, zorder=1)

    # Draw all aircraft routes (lighter, in background)
    route_count = 0
    for route in chromosome:
        if route_count >= max_routes:
            break
        if len(route) > 1:
            for i in range(len(route) - 1):
                origin = route[i]
                dest = route[i + 1]
                if origin in positions and dest in positions:
                    x1, y1 = positions[origin]
                    x2, y2 = positions[dest]
                    ax.plot([x1, x2], [y1, y2], "gray", alpha=0.1, linewidth=0.5, zorder=0)
        route_count += 1

    # Draw airports
    for code, (x, y) in positions.items():
        ax.plot(x, y, "ro", markersize=10, zorder=2)
        ax.text(
            x,
            y + 0.05,
            code,
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            zorder=3,
        )

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Route Network (showing top {min(len(route_usage), max_routes)} used routes)")

    # Add legend
    if route_usage:
        max_usage = max(usage for _, usage in route_usage.items())
        legend_elements = [
            mpatches.Patch(color="blue", alpha=0.8, label=f"High usage ({max_usage:.0f} pax)"),
            mpatches.Patch(color="blue", alpha=0.4, label="Low usage"),
            mpatches.Patch(color="gray", alpha=0.1, label="Unused routes"),
        ]
        ax.legend(handles=legend_elements, loc="upper right")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Routes plot saved to {save_path}")
    else:
        plt.show()


def plot_aircraft_routes(
    chromosome: List[List[str]],
    stats: Dict,
    airport_codes: List[str],
    save_path: str = None,
    max_aircraft: int = 20,
):
    """
    Plot individual aircraft routes.

    Args:
        chromosome: Best chromosome
        stats: Statistics dictionary
        airport_codes: List of airport codes
        save_path: Optional path to save the figure
        max_aircraft: Maximum number of aircraft to display
    """
    # Find aircraft with allocations
    aircraft_allocations = defaultdict(list)
    if stats.get("allocations"):
        for origin, dest, pax, aircraft_id, stops in stats["allocations"]:
            aircraft_allocations[aircraft_id].append((origin, dest, pax, stops))

    # Sort by total passengers allocated
    aircraft_totals = {
        aid: sum(pax for _, _, pax, _ in allocs) for aid, allocs in aircraft_allocations.items()
    }
    sorted_aircraft = sorted(aircraft_totals.items(), key=lambda x: x[1], reverse=True)

    n_aircraft = min(len(sorted_aircraft), max_aircraft)
    if n_aircraft == 0:
        print("No aircraft with allocations to display")
        return

    fig, axes = plt.subplots((n_aircraft + 2) // 3, 3, figsize=(15, 5 * ((n_aircraft + 2) // 3)))
    fig.suptitle("Top Aircraft Routes with Allocations", fontsize=16, fontweight="bold")

    if n_aircraft == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for idx, (aircraft_id, total_pax) in enumerate(sorted_aircraft[:n_aircraft]):
        ax = axes[idx]
        route = chromosome[aircraft_id]
        allocations = aircraft_allocations[aircraft_id]

        # Create position map
        n_airports = len(airport_codes)
        angles = np.linspace(0, 2 * np.pi, n_airports, endpoint=False)
        radius = 1.0
        positions = {}
        for i, code in enumerate(airport_codes):
            x = radius * np.cos(angles[i])
            y = radius * np.sin(angles[i])
            positions[code] = (x, y)

        # Draw route
        for i in range(len(route) - 1):
            origin = route[i]
            dest = route[i + 1]
            if origin in positions and dest in positions:
                x1, y1 = positions[origin]
                x2, y2 = positions[dest]
                ax.plot([x1, x2], [y1, y2], "b-", alpha=0.5, linewidth=1, zorder=1)

        # Highlight allocations
        for origin, dest, pax, stops in allocations:
            if origin in positions and dest in positions:
                x1, y1 = positions[origin]
                x2, y2 = positions[dest]
                ax.plot([x1, x2], [y1, y2], "r-", alpha=0.8, linewidth=3, zorder=2)
                # Add label
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(
                    mid_x,
                    mid_y,
                    f"{pax}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                )

        # Draw airports
        for code, (x, y) in positions.items():
            if code in route:
                ax.plot(x, y, "ro", markersize=8, zorder=3)
                ax.text(
                    x,
                    y + 0.05,
                    code,
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    fontweight="bold",
                    zorder=4,
                )

        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"Aircraft {aircraft_id}\n{total_pax} passengers", fontsize=10)

    # Hide unused subplots
    for idx in range(n_aircraft, len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Aircraft routes plot saved to {save_path}")
    else:
        plt.show()


def visualize_results(
    chromosome: List[List[str]],
    stats: Dict,
    airport_codes: List[str],
    save_dir: str = None,
    evolution_history: Optional[List[Dict]] = None,
):
    """
    Create all visualizations for the genetic algorithm results.

    Args:
        chromosome: Best chromosome
        stats: Statistics dictionary
        airport_codes: List of airport codes
        save_dir: Optional directory to save figures
        evolution_history: Optional evolution history for time-series plots
    """
    print("\n" + "=" * 80)
    print("VISUALIZING RESULTS")
    print("=" * 80)

    if save_dir:
        import os

        os.makedirs(save_dir, exist_ok=True)
        stats_path = os.path.join(save_dir, "statistics.png")
        routes_path = os.path.join(save_dir, "routes_network.png")
        aircraft_path = os.path.join(save_dir, "aircraft_routes.png")
        fitness_decay_path = os.path.join(save_dir, "fitness_decay.png")
        metrics_time_path = os.path.join(save_dir, "metrics_over_time.png")
        diversity_path = os.path.join(save_dir, "population_diversity.png")
        convergence_path = os.path.join(save_dir, "convergence_analysis.png")
        mutation_decay_path = os.path.join(save_dir, "mutation_rate_decay.png")
        comprehensive_path = os.path.join(save_dir, "comprehensive_evolution.png")
        summary_path = os.path.join(save_dir, "summary.txt")
    else:
        stats_path = None
        routes_path = None
        aircraft_path = None
        fitness_decay_path = None
        metrics_time_path = None
        diversity_path = None
        convergence_path = None
        mutation_decay_path = None
        comprehensive_path = None
        summary_path = None

    # Plot statistics
    print("Generating statistics plot...")
    plot_statistics(stats, save_path=stats_path)

    # Plot route network
    print("Generating route network plot...")
    plot_routes(chromosome, stats, airport_codes, save_path=routes_path)

    # Plot individual aircraft routes
    print("Generating aircraft routes plot...")
    plot_aircraft_routes(chromosome, stats, airport_codes, save_path=aircraft_path)

    # Plot evolution history if available
    if evolution_history:
        print("Generating evolution plots...")
        plot_fitness_decay(evolution_history, save_path=fitness_decay_path)
        plot_metrics_over_time(evolution_history, save_path=metrics_time_path)
        plot_population_diversity(evolution_history, save_path=diversity_path)
        plot_convergence_analysis(evolution_history, save_path=convergence_path)
        plot_mutation_rate_decay(evolution_history, save_path=mutation_decay_path)
        plot_comprehensive_evolution(evolution_history, save_path=comprehensive_path)

    # Generate summary report
    print("Generating summary report...")
    save_summary_report(chromosome, stats, evolution_history, save_path=summary_path)

    print("\nVisualization complete!")


def plot_fitness_decay(evolution_history: List[Dict], save_path: str = None):
    """
    Plot fitness decay over generations.

    Args:
        evolution_history: List of dictionaries with evolution metrics per generation
        save_path: Optional path to save the figure
    """
    if not evolution_history:
        print("No evolution history to plot")
        return

    generations = [entry["generation"] for entry in evolution_history]
    best_fitness = [entry["best_fitness"] for entry in evolution_history]
    avg_fitness = [entry["avg_fitness"] for entry in evolution_history]
    std_fitness = [entry["std_fitness"] for entry in evolution_history]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Fitness Decay Over Generations", fontsize=16, fontweight="bold")

    # Plot best fitness
    ax.plot(generations, best_fitness, "b-", label="Best Fitness", linewidth=2, marker="o", markersize=4)

    # Plot average fitness with shaded std region
    ax.plot(generations, avg_fitness, "g-", label="Average Fitness", linewidth=2, marker="s", markersize=4)
    ax.fill_between(
        generations,
        [avg - std for avg, std in zip(avg_fitness, std_fitness)],
        [avg + std for avg, std in zip(avg_fitness, std_fitness)],
        alpha=0.2,
        color="green",
        label="±1 Std Dev",
    )

    # Mark convergence point if applicable
    if len(evolution_history) > 1:
        # Check if fitness stopped improving significantly
        last_improvement = best_fitness[-1]
        if len(best_fitness) >= 10:
            recent_avg = np.mean(best_fitness[-10:])
            if abs(last_improvement - recent_avg) < 50:  # Threshold for convergence
                ax.axvline(x=generations[-1], color="r", linestyle="--", alpha=0.5, label="Convergence")

    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness Score")
    ax.set_title("Fitness Evolution")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Fitness decay plot saved to {save_path}")
    else:
        plt.show()


def plot_metrics_over_time(evolution_history: List[Dict], save_path: str = None):
    """
    Plot key metrics over time.

    Args:
        evolution_history: List of dictionaries with evolution metrics per generation
        save_path: Optional path to save the figure
    """
    if not evolution_history:
        print("No evolution history to plot")
        return

    generations = [entry["generation"] for entry in evolution_history]
    unserved = [entry["unserved_passengers"] for entry in evolution_history]
    stops = [entry["total_stops"] for entry in evolution_history]
    flights = [entry["total_flights"] for entry in evolution_history]
    mutation_rate = [entry["mutation_rate"] for entry in evolution_history]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Metrics Over Time", fontsize=16, fontweight="bold")

    # Unserved passengers
    axes[0, 0].plot(generations, unserved, "r-", linewidth=2, marker="o", markersize=3)
    axes[0, 0].set_xlabel("Generation")
    axes[0, 0].set_ylabel("Unserved Passengers")
    axes[0, 0].set_title("Unserved Passengers Over Time")
    axes[0, 0].grid(True, alpha=0.3)

    # Total stops
    axes[0, 1].plot(generations, stops, "orange", linewidth=2, marker="s", markersize=3)
    axes[0, 1].set_xlabel("Generation")
    axes[0, 1].set_ylabel("Total Stops")
    axes[0, 1].set_title("Total Stops Over Time")
    axes[0, 1].grid(True, alpha=0.3)

    # Total flights
    axes[1, 0].plot(generations, flights, "b-", linewidth=2, marker="^", markersize=3)
    axes[1, 0].set_xlabel("Generation")
    axes[1, 0].set_ylabel("Total Flights")
    axes[1, 0].set_title("Total Flights Over Time")
    axes[1, 0].grid(True, alpha=0.3)

    # Mutation rate decay
    axes[1, 1].plot(generations, mutation_rate, "purple", linewidth=2, marker="d", markersize=3)
    axes[1, 1].set_xlabel("Generation")
    axes[1, 1].set_ylabel("Mutation Rate")
    axes[1, 1].set_title("Mutation Rate Decay")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Metrics over time plot saved to {save_path}")
    else:
        plt.show()


def plot_population_diversity(evolution_history: List[Dict], save_path: str = None):
    """
    Plot population diversity metrics.

    Args:
        evolution_history: List of dictionaries with evolution metrics per generation
        save_path: Optional path to save the figure
    """
    if not evolution_history:
        print("No evolution history to plot")
        return

    generations = [entry["generation"] for entry in evolution_history]
    std_fitness = [entry["std_fitness"] for entry in evolution_history]
    best_fitness = [entry["best_fitness"] for entry in evolution_history]
    avg_fitness = [entry["avg_fitness"] for entry in evolution_history]
    fitness_gap = [best - avg for best, avg in zip(best_fitness, avg_fitness)]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Population Diversity Analysis", fontsize=16, fontweight="bold")

    # Standard deviation (diversity measure)
    axes[0].plot(generations, std_fitness, "b-", linewidth=2, marker="o", markersize=4)
    axes[0].set_xlabel("Generation")
    axes[0].set_ylabel("Fitness Standard Deviation")
    axes[0].set_title("Population Diversity (Std Dev)")
    axes[0].grid(True, alpha=0.3)

    # Best vs Average gap
    axes[1].plot(generations, fitness_gap, "g-", linewidth=2, marker="s", markersize=4)
    axes[1].set_xlabel("Generation")
    axes[1].set_ylabel("Fitness Gap (Best - Avg)")
    axes[1].set_title("Best vs Average Fitness Gap")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Population diversity plot saved to {save_path}")
    else:
        plt.show()


def plot_convergence_analysis(evolution_history: List[Dict], save_path: str = None):
    """
    Plot convergence analysis.

    Args:
        evolution_history: List of dictionaries with evolution metrics per generation
        save_path: Optional path to save the figure
    """
    if not evolution_history or len(evolution_history) < 2:
        print("Not enough evolution history for convergence analysis")
        return

    generations = [entry["generation"] for entry in evolution_history]
    best_fitness = [entry["best_fitness"] for entry in evolution_history]

    # Calculate improvement rate (negative derivative)
    improvement_rate = []
    for i in range(1, len(best_fitness)):
        improvement = best_fitness[i - 1] - best_fitness[i]  # Positive means improvement
        improvement_rate.append(improvement)

    improvement_generations = generations[1:]

    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle("Convergence Analysis", fontsize=16, fontweight="bold")

    # Fitness over time
    axes[0].plot(generations, best_fitness, "b-", linewidth=2, marker="o", markersize=4)
    axes[0].set_xlabel("Generation")
    axes[0].set_ylabel("Best Fitness")
    axes[0].set_title("Fitness Evolution")
    axes[0].grid(True, alpha=0.3)

    # Improvement rate
    axes[1].plot(improvement_generations, improvement_rate, "r-", linewidth=2, marker="s", markersize=4)
    axes[1].axhline(y=0, color="k", linestyle="--", alpha=0.5)
    axes[1].set_xlabel("Generation")
    axes[1].set_ylabel("Fitness Improvement per Generation")
    axes[1].set_title("Improvement Rate (Lower is Better)")
    axes[1].grid(True, alpha=0.3)

    # Highlight stagnation periods (low improvement)
    if improvement_rate:
        threshold = np.percentile(improvement_rate, 25)  # Bottom 25% improvement
        for i, (gen, rate) in enumerate(zip(improvement_generations, improvement_rate)):
            if rate < threshold:
                axes[1].axvline(x=gen, color="orange", alpha=0.2, linewidth=0.5)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Convergence analysis plot saved to {save_path}")
    else:
        plt.show()


def plot_mutation_rate_decay(evolution_history: List[Dict], save_path: str = None):
    """
    Plot mutation rate decay schedule.

    Args:
        evolution_history: List of dictionaries with evolution metrics per generation
        save_path: Optional path to save the figure
    """
    if not evolution_history:
        print("No evolution history to plot")
        return

    generations = [entry["generation"] for entry in evolution_history]
    mutation_rate = [entry["mutation_rate"] for entry in evolution_history]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Mutation Rate Decay Schedule", fontsize=16, fontweight="bold")

    ax.plot(generations, mutation_rate, "purple", linewidth=2, marker="o", markersize=4)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Mutation Rate")
    ax.set_title("Annealing Schedule")
    ax.grid(True, alpha=0.3)

    # Add annotation for initial and final rates
    if mutation_rate:
        ax.annotate(
            f"Initial: {mutation_rate[0]:.4f}",
            xy=(generations[0], mutation_rate[0]),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )
        if len(mutation_rate) > 1:
            ax.annotate(
                f"Final: {mutation_rate[-1]:.4f}",
                xy=(generations[-1], mutation_rate[-1]),
                xytext=(10, -20),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Mutation rate decay plot saved to {save_path}")
    else:
        plt.show()


def plot_comprehensive_evolution(evolution_history: List[Dict], save_path: str = None):
    """
    Create comprehensive evolution dashboard.

    Args:
        evolution_history: List of dictionaries with evolution metrics per generation
        save_path: Optional path to save the figure
    """
    if not evolution_history:
        print("No evolution history to plot")
        return

    generations = [entry["generation"] for entry in evolution_history]
    best_fitness = [entry["best_fitness"] for entry in evolution_history]
    avg_fitness = [entry["avg_fitness"] for entry in evolution_history]
    std_fitness = [entry["std_fitness"] for entry in evolution_history]
    unserved = [entry["unserved_passengers"] for entry in evolution_history]
    stops = [entry["total_stops"] for entry in evolution_history]
    flights = [entry["total_flights"] for entry in evolution_history]
    mutation_rate = [entry["mutation_rate"] for entry in evolution_history]

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("Comprehensive Evolution Dashboard", fontsize=18, fontweight="bold")

    # Create grid layout
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. Fitness decay (top left, spans 2 columns)
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(generations, best_fitness, "b-", label="Best", linewidth=2, marker="o", markersize=3)
    ax1.plot(generations, avg_fitness, "g-", label="Average", linewidth=2, marker="s", markersize=3)
    ax1.fill_between(
        generations,
        [avg - std for avg, std in zip(avg_fitness, std_fitness)],
        [avg + std for avg, std in zip(avg_fitness, std_fitness)],
        alpha=0.2,
        color="green",
    )
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Fitness")
    ax1.set_title("Fitness Evolution")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Mutation rate (top right)
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.plot(generations, mutation_rate, "purple", linewidth=2, marker="d", markersize=3)
    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Mutation Rate")
    ax2.set_title("Mutation Rate")
    ax2.grid(True, alpha=0.3)

    # 3. Unserved passengers
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(generations, unserved, "r-", linewidth=2, marker="o", markersize=3)
    ax3.set_xlabel("Generation")
    ax3.set_ylabel("Unserved Passengers")
    ax3.set_title("Unserved Passengers")
    ax3.grid(True, alpha=0.3)

    # 4. Total stops
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(generations, stops, "orange", linewidth=2, marker="s", markersize=3)
    ax4.set_xlabel("Generation")
    ax4.set_ylabel("Total Stops")
    ax4.set_title("Total Stops")
    ax4.grid(True, alpha=0.3)

    # 5. Total flights
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.plot(generations, flights, "b-", linewidth=2, marker="^", markersize=3)
    ax5.set_xlabel("Generation")
    ax5.set_ylabel("Total Flights")
    ax5.set_title("Total Flights")
    ax5.grid(True, alpha=0.3)

    # 6. Population diversity (std)
    ax6 = fig.add_subplot(gs[2, 0])
    ax6.plot(generations, std_fitness, "cyan", linewidth=2, marker="o", markersize=3)
    ax6.set_xlabel("Generation")
    ax6.set_ylabel("Std Dev")
    ax6.set_title("Population Diversity")
    ax6.grid(True, alpha=0.3)

    # 7. Fitness gap
    fitness_gap = [best - avg for best, avg in zip(best_fitness, avg_fitness)]
    ax7 = fig.add_subplot(gs[2, 1])
    ax7.plot(generations, fitness_gap, "magenta", linewidth=2, marker="s", markersize=3)
    ax7.set_xlabel("Generation")
    ax7.set_ylabel("Fitness Gap")
    ax7.set_title("Best - Average Gap")
    ax7.grid(True, alpha=0.3)

    # 8. Improvement rate
    improvement_rate = []
    improvement_gens = []
    for i in range(1, len(best_fitness)):
        improvement = best_fitness[i - 1] - best_fitness[i]
        improvement_rate.append(improvement)
        improvement_gens.append(generations[i])
    ax8 = fig.add_subplot(gs[2, 2])
    if improvement_rate:
        ax8.plot(improvement_gens, improvement_rate, "red", linewidth=2, marker="^", markersize=3)
        ax8.axhline(y=0, color="k", linestyle="--", alpha=0.5)
    ax8.set_xlabel("Generation")
    ax8.set_ylabel("Improvement")
    ax8.set_title("Improvement Rate")
    ax8.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Comprehensive evolution plot saved to {save_path}")
    else:
        plt.show()


def save_summary_report(
    chromosome: List[List[str]],
    stats: Dict,
    evolution_history: Optional[List[Dict]] = None,
    save_path: str = None,
):
    """
    Save a comprehensive text summary of results.

    Args:
        chromosome: Best chromosome (list of aircraft routes)
        stats: Statistics dictionary
        evolution_history: Optional evolution history
        save_path: Path to save the summary file
    """
    if save_path is None:
        save_path = "results/summary.txt"

    import os

    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

    with open(save_path, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("GENETIC ALGORITHM RESULTS SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        # Basic statistics
        f.write("SOLUTION STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Fitness Score: {stats.get('fitness_score', 'N/A'):,.2f}\n")
        f.write(f"Unserved Passengers: {stats.get('unserved_passengers', 0):,}\n")
        f.write(f"Total Stops: {stats.get('total_stops', 0):,}\n")
        f.write(f"Total Flights: {stats.get('total_flights', 0):,}\n\n")

        # Calculate additional metrics
        allocations = stats.get("allocations", [])
        total_served = sum(pax for _, _, pax, _, _ in allocations)
        total_unserved = stats.get("unserved_passengers", 0)
        total_demand = total_served + total_unserved
        service_rate = (total_served / total_demand * 100) if total_demand > 0 else 0

        f.write("PASSENGER ALLOCATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Demand: {total_demand:,}\n")
        f.write(f"Served Passengers: {total_served:,}\n")
        f.write(f"Unserved Passengers: {total_unserved:,}\n")
        f.write(f"Service Rate: {service_rate:.2f}%\n\n")

        # Flight and leg statistics
        f.write("FLIGHT STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Number of Unique Flights: {stats.get('total_flights', 0):,}\n")

        # Count unique legs
        unique_legs = set()
        if allocations:
            for origin, dest, pax, aircraft_id, stops in allocations:
                route = chromosome[aircraft_id] if aircraft_id < len(chromosome) else []
                try:
                    origin_idx = route.index(origin)
                    dest_idx = route.index(dest)
                    if dest_idx > origin_idx:
                        for i in range(origin_idx, dest_idx):
                            leg = (route[i], route[i + 1])
                            unique_legs.add(leg)
                except (ValueError, IndexError):
                    pass

        f.write(f"Number of Unique Legs: {len(unique_legs):,}\n")

        # Count aircraft used
        aircraft_used = set()
        if allocations:
            for _, _, _, aircraft_id, _ in allocations:
                aircraft_used.add(aircraft_id)
        f.write(f"Number of Aircraft Used: {len(aircraft_used):,}\n")
        f.write(f"Total Number of Routes: {len(chromosome):,}\n\n")

        # Route statistics
        route_lengths = [len(route) for route in chromosome if route]
        if route_lengths:
            avg_route_length = np.mean(route_lengths)
            max_route_length = max(route_lengths)
            min_route_length = min(route_lengths)
            f.write("ROUTE STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Average Route Length: {avg_route_length:.2f} airports\n")
            f.write(f"Minimum Route Length: {min_route_length} airports\n")
            f.write(f"Maximum Route Length: {max_route_length} airports\n\n")

        # Evolution statistics
        if evolution_history:
            f.write("EVOLUTION STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Generations Run: {len(evolution_history)}\n")

            if len(evolution_history) > 1:
                initial_fitness = evolution_history[0]["best_fitness"]
                final_fitness = evolution_history[-1]["best_fitness"]
                fitness_improvement = initial_fitness - final_fitness
                improvement_percent = (fitness_improvement / initial_fitness * 100) if initial_fitness > 0 else 0

                f.write(f"Initial Fitness: {initial_fitness:,.2f}\n")
                f.write(f"Final Fitness: {final_fitness:,.2f}\n")
                f.write(f"Fitness Improvement: {fitness_improvement:,.2f} ({improvement_percent:.2f}%)\n")

                # Check for convergence
                if len(evolution_history) >= 10:
                    recent_improvements = []
                    for i in range(max(1, len(evolution_history) - 10), len(evolution_history)):
                        if i > 0:
                            improvement = evolution_history[i - 1]["best_fitness"] - evolution_history[i]["best_fitness"]
                            recent_improvements.append(improvement)
                    avg_recent_improvement = np.mean(recent_improvements) if recent_improvements else 0
                    f.write(f"Average Recent Improvement (last 10 gens): {avg_recent_improvement:.2f}\n")

                # Mutation rate info
                initial_mutation = evolution_history[0]["mutation_rate"]
                final_mutation = evolution_history[-1]["mutation_rate"]
                f.write(f"Initial Mutation Rate: {initial_mutation:.4f}\n")
                f.write(f"Final Mutation Rate: {final_mutation:.4f}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF SUMMARY\n")
        f.write("=" * 80 + "\n")

    print(f"Summary report saved to {save_path}")
