"""
Visualization module for genetic algorithm results.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

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
):
    """
    Create all visualizations for the genetic algorithm results.

    Args:
        chromosome: Best chromosome
        stats: Statistics dictionary
        airport_codes: List of airport codes
        save_dir: Optional directory to save figures
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
    else:
        stats_path = None
        routes_path = None
        aircraft_path = None

    # Plot statistics
    print("Generating statistics plot...")
    plot_statistics(stats, save_path=stats_path)

    # Plot route network
    print("Generating route network plot...")
    plot_routes(chromosome, stats, airport_codes, save_path=routes_path)

    # Plot individual aircraft routes
    print("Generating aircraft routes plot...")
    plot_aircraft_routes(chromosome, stats, airport_codes, save_path=aircraft_path)

    print("\nVisualization complete!")
