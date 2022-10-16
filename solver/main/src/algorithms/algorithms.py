from .greedyheuristic import greedy_heuristic_solver
from .simulatedannealing import simulated_annealing_with_random

algorithms = {
    "1": {
        "algorithm": greedy_heuristic_solver,
        "description": "Greedy Heuristic algorithm"
    },
    "2": {
        "algorithm": simulated_annealing_with_random,
        "description": "Simulated Annealing algorithm with random initialisation"
    }
}
