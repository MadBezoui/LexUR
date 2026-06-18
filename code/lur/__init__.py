"""Leximax Universal-Regret (LUR) Core — reference implementation and experiments.

Modules:
    problems    : multi-objective Pareto-front candidate-set generators
    methods     : selection methods (LUR + classical + robust-MCDA baselines)
    metrics     : out-of-class loss, worst-case regret, agreement, etc.
    stats       : Friedman / Nemenyi / Wilcoxon / Cliff's delta
    experiments : benchmark orchestration
    smartgrid   : 6-objective stochastic dispatch decision case study
"""
__all__ = ["problems", "methods", "metrics", "stats", "experiments", "smartgrid"]
__version__ = "1.0.0"
