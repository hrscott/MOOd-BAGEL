from design_framework.core.base import Oracle


class FoldingOracle(Oracle):
    def __init__(self, backend: str = 'colabfold'):
        self.backend = backend

    def compute(self, chains: dict) -> dict:
        # chains: dict of chain name -> sequence (or fixed structure)
        # For now, return a stub output
        return {
            'coords': {name: None for name in chains},
            'pLDDT': {name: 0.0 for name in chains},
            'PAE': None,
            'pTM': 0.0,
        }
