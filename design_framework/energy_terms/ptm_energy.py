from design_framework.core.base import EnergyTerm


class PTMEnergy(EnergyTerm):
    """
    Rewards high pTM by lowering energy. Expects oracle_outputs['pTM'] in 0..1.
    """

    def evaluate(self, oracle_outputs: dict, system_state: dict) -> float:
        ptm = oracle_outputs.get("pTM", 0.0)
        return -(ptm * self.weight)
