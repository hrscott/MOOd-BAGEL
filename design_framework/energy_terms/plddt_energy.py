from typing import Dict
from design_framework.core.base import EnergyTerm

class PLDDTEnergy(EnergyTerm):
    """
    Negative-energy reward for high pLDDT. Higher pLDDT -> lower energy.
    Expects oracle_outputs['pLDDT'] as dict: chain_name -> float (0..1 or 0..100).
    """
    def __init__(self, weight: float = 1.0, scale: float = 1.0):
        super().__init__(weight)
        self.scale = scale  # if pLDDT is 0..100 set scale=0.01

    def evaluate(self, oracle_outputs: Dict, system_state: Dict) -> float:
        plddts = oracle_outputs.get("pLDDT", {})
        if not plddts:
            return 0.0
        # negative because higher pLDDT should reduce energy
        total = 0.0
        for _, p in plddts.items():
            total += -(p * self.scale) * self.weight
        return total
