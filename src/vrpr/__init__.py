"""VRPR - Vehicle Routing Problem with Restricted edges.

Multi-vehicle routing from a single depot (node 0) where each client is
visited exactly once and the total travel cost is minimised. Two business
constraints sit on top of the classic VRP:

- closed edges   : some roads are impassable (``close=True``);
- surcharged edges: some roads are usable but cost more (``surcout=True``).

This package holds the implementation extracted from ``notebooks/final_nb.ipynb``
so the algorithms can be imported, reused and tested outside the notebook.
"""

from .graph import random_graph
from .core import cout_solution, voisinage
from .greedy import glouton, multi_start_glouton
from .tabu import recherche_tabou, multi_start_tabou
from .annealing import recuit_simule, multi_start_recuit
from .genetic import genetic_algorithm_vrp_advanced

__all__ = [
    "random_graph",
    "cout_solution",
    "voisinage",
    "glouton",
    "multi_start_glouton",
    "recherche_tabou",
    "multi_start_tabou",
    "recuit_simule",
    "multi_start_recuit",
    "genetic_algorithm_vrp_advanced",
]
