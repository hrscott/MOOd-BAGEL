from design_framework.core.base import EnergyTerm


class PAEEnergy(EnergyTerm):
    """
    Penalizes high PAE (uncertainty). For now, if PAE matrix is None, returns 0.
    If available (NxN), uses mean PAE (assumed 0..30 or 0..31) scaled to ~0..1.
    """

    def __init__(self, weight: float = 1.0, scale: float = 1 / 31.0):
        super().__init__(weight)
        self.scale = scale

    def evaluate(self, oracle_outputs: dict, system_state: dict) -> float:
        pae = oracle_outputs.get("PAE", None)
        if pae is None:
            return 0.0
        # naive average
        try:
            import numpy as np

            mean_pae = float(np.mean(pae))
        except Exception:
            return 0.0
        return (mean_pae * self.scale) * self.weight  # higher uncertainty -> higher energy
