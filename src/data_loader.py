"""
Data loading module for parsing CSV files.
"""

import os
from typing import Dict, List, Tuple

import pandas as pd


def load_airports(data_dir: str = "data") -> List[str]:
    """
    Load airport codes from airports.csv.

    Args:
        data_dir: Directory containing the CSV files

    Returns:
        List of airport codes (e.g., ['MA', 'BE', 'FO', ...])
    """
    filepath = os.path.join(data_dir, "airports.csv")
    # Use keep_default_na=False to prevent 'NA' from being read as NaN
    df = pd.read_csv(filepath, keep_default_na=False)
    # Filter out empty strings and convert to list
    codes = [code for code in df["code"].tolist() if code and str(code).strip()]
    return codes


def load_route_durations(data_dir: str = "data") -> Dict[Tuple[str, str], int]:
    """
    Load route durations from routes.csv.

    Args:
        data_dir: Directory containing the CSV files

    Returns:
        Dictionary mapping (origin, dest) tuples to duration in minutes
        Example: {('MA', 'BE'): 120, ('BE', 'FO'): 120, ...}
    """
    filepath = os.path.join(data_dir, "routes.csv")
    # Use keep_default_na=False to prevent 'NA' from being read as NaN
    df = pd.read_csv(filepath, keep_default_na=False)
    route_dict = {}
    for _, row in df.iterrows():
        # Skip rows with empty values
        origin = str(row["origin"]).strip()
        dest = str(row["dest"]).strip()
        duration = row["duration_min"]
        if not origin or not dest or pd.isna(duration):
            continue
        route_dict[(origin, dest)] = int(duration)
    return route_dict


def load_demand(data_dir: str = "data") -> List[Tuple[str, str, int]]:
    """
    Load passenger demand from demand_od.csv.

    Args:
        data_dir: Directory containing the CSV files

    Returns:
        List of (origin, dest, passengers) tuples
        Example: [('MA', 'BE', 350), ('FO', 'BH', 600), ...]
    """
    filepath = os.path.join(data_dir, "demand_od.csv")
    # Use keep_default_na=False to prevent 'NA' from being read as NaN
    df = pd.read_csv(filepath, keep_default_na=False)
    demand_list = []
    for _, row in df.iterrows():
        # Skip rows with empty values
        origin = str(row["origin"]).strip()
        dest = str(row["dest"]).strip()
        pax = row["pax_daily"]
        if not origin or not dest or pd.isna(pax):
            continue
        demand_list.append((origin, dest, int(pax)))
    return demand_list


def load_all_data(data_dir: str = "data"):
    """
    Load all data files and return as a tuple.

    Args:
        data_dir: Directory containing the CSV files

    Returns:
        Tuple of (airport_codes, route_durations, demand_list)
    """
    airports = load_airports(data_dir)
    routes = load_route_durations(data_dir)
    demand = load_demand(data_dir)
    return airports, routes, demand
