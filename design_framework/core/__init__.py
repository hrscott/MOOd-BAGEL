"""
Public API for the lightweight design_framework core.

For now we only expose the minimal base interfaces:
  - Oracle
  - EnergyTerm
  - MutationProtocol
  - Minimizer

Integration with the full BAGEL System/State types is intentionally
deferred so that design_framework can be used in environments where
the heavy `bagel` dependencies (biotite, boileroom, etc.) are not
installed yet.
"""

from .base import Oracle, EnergyTerm, MutationProtocol, Minimizer

__all__ = [
    "Oracle",
    "EnergyTerm",
    "MutationProtocol",
    "Minimizer",
]
