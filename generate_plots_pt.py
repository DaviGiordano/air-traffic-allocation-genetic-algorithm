"""
Script to generate plots in Brazilian Portuguese from saved results.
"""

import pickle
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_fitness_decay_pt(evolution_history: list, save_path: str = None):
    """
    Plot fitness decay over generations in Brazilian Portuguese.
    
    Args:
        evolution_history: List of dictionaries with evolution metrics per generation
        save_path: Optional path to save the figure
    """
    if not evolution_history:
        print("Sem histórico de evolução para plotar")
        return

    generations = [entry["generation"] for entry in evolution_history]
    best_fitness = [entry["best_fitness"] for entry in evolution_history]
    avg_fitness = [entry["avg_fitness"] for entry in evolution_history]
    std_fitness = [entry["std_fitness"] for entry in evolution_history]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Decaimento da Fitness ao Longo das Gerações", fontsize=16, fontweight="bold")

    # Plot best fitness
    ax.plot(generations, best_fitness, "b-", label="Melhor Fitness", linewidth=2, marker="o", markersize=4)

    # Plot average fitness with shaded std region
    ax.plot(generations, avg_fitness, "g-", label="Fitness Média", linewidth=2, marker="s", markersize=4)
    ax.fill_between(
        generations,
        [avg - std for avg, std in zip(avg_fitness, std_fitness)],
        [avg + std for avg, std in zip(avg_fitness, std_fitness)],
        alpha=0.2,
        color="green",
        label="±1 Desvio Padrão",
    )

    # Convergence line removed as requested

    ax.set_xlabel("Geração")
    ax.set_ylabel("Pontuação de Fitness")
    ax.set_title("Evolução da Fitness")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Gráfico de decaimento da Fitness salvo em {save_path}")
    else:
        plt.show()
    plt.close()


def plot_metrics_over_time_pt(evolution_history: list, save_path: str = None):
    """
    Plot key metrics over time in Brazilian Portuguese.
    
    Args:
        evolution_history: List of dictionaries with evolution metrics per generation
        save_path: Optional path to save the figure
    """
    if not evolution_history:
        print("Sem histórico de evolução para plotar")
        return

    generations = [entry["generation"] for entry in evolution_history]
    unserved = [entry["unserved_passengers"] for entry in evolution_history]
    stops = [entry["total_stops"] for entry in evolution_history]
    flights = [entry["total_flights"] for entry in evolution_history]
    mutation_rate = [entry["mutation_rate"] for entry in evolution_history]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Métricas ao Longo do Tempo", fontsize=16, fontweight="bold")

    # Unserved passengers
    axes[0, 0].plot(generations, unserved, "r-", linewidth=2, marker="o", markersize=3)
    axes[0, 0].set_xlabel("Geração")
    axes[0, 0].set_ylabel("Passageiros Não Atendidos")
    axes[0, 0].set_title("Passageiros Não Atendidos ao Longo do Tempo")
    axes[0, 0].grid(True, alpha=0.3)

    # Total stops
    axes[0, 1].plot(generations, stops, "orange", linewidth=2, marker="s", markersize=3)
    axes[0, 1].set_xlabel("Geração")
    axes[0, 1].set_ylabel("Total de Escalas")
    axes[0, 1].set_title("Total de Escalas ao Longo do Tempo")
    axes[0, 1].grid(True, alpha=0.3)

    # Total flights
    axes[1, 0].plot(generations, flights, "b-", linewidth=2, marker="^", markersize=3)
    axes[1, 0].set_xlabel("Geração")
    axes[1, 0].set_ylabel("Total de Voos")
    axes[1, 0].set_title("Total de Voos ao Longo do Tempo")
    axes[1, 0].grid(True, alpha=0.3)

    # Mutation rate decay
    axes[1, 1].plot(generations, mutation_rate, "purple", linewidth=2, marker="d", markersize=3)
    axes[1, 1].set_xlabel("Geração")
    axes[1, 1].set_ylabel("Taxa de Mutação")
    axes[1, 1].set_title("Decaimento da Taxa de Mutação")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Gráfico de métricas ao longo do tempo salvo em {save_path}")
    else:
        plt.show()
    plt.close()


def main():
    """Main function to load results and generate plots."""
    results_dir = Path("results")
    evolution_history_path = results_dir / "evolution_history.pkl"
    
    if not evolution_history_path.exists():
        print(f"Erro: Arquivo {evolution_history_path} não encontrado!")
        return
    
    print(f"Carregando resultados de {evolution_history_path}...")
    with open(evolution_history_path, "rb") as f:
        evolution_history = pickle.load(f)
    
    print(f"Carregado histórico de {len(evolution_history)} gerações")
    
    # Generate fitness decay plot
    print("\nGerando gráfico de decaimento da Fitness...")
    fitness_decay_path = results_dir / "fitness_decay.png"
    plot_fitness_decay_pt(evolution_history, save_path=str(fitness_decay_path))
    
    # Generate metrics over time plot
    print("Gerando gráfico de métricas ao longo do tempo...")
    metrics_time_path = results_dir / "metrics_over_time.png"
    plot_metrics_over_time_pt(evolution_history, save_path=str(metrics_time_path))
    
    print("\nConcluído! Gráficos salvos em:")
    print(f"  - {fitness_decay_path}")
    print(f"  - {metrics_time_path}")


if __name__ == "__main__":
    main()

