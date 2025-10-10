from abc import ABC, abstractmethod


class Oracle(ABC):
    @abstractmethod
    def compute(self, chains: dict):
        """Given chain sequences (and optionally fixed structures), return a dict of model outputs (coords, embeddings, etc.)."""
        pass


class EnergyTerm(ABC):
    def __init__(self, weight: float = 1.0):
        self.weight = weight

    @abstractmethod
    def evaluate(self, oracle_outputs: dict, system_state: dict) -> float:
        """Return the scalar energy (or negative score) contribution."""
        pass


class MutationProtocol(ABC):
    @abstractmethod
    def propose(self, sequences: dict, oracle_outputs: dict) -> dict:
        """Given current sequences & oracle outputs, return a new proposed sequences dict."""
        pass


class Minimizer(ABC):
    @abstractmethod
    def run(self, system) -> dict:
        """Run optimization, return best sequences + metadata."""
        pass
