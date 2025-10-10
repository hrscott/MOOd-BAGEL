import math
import random
from copy import deepcopy
from typing import Dict, List

class SimpleMinimizer:
    """
    Minimal Monte Carlo + linear annealing minimizer.
    Expects `system` dict with keys:
      - sequences: Dict[str, str]
      - oracles: List[Oracle]
      - mutation_protocols: List[MutationProtocol]
      - energy_terms: List[EnergyTerm]
    """
    def __init__(self, steps: int = 500, t_init: float = 1.0, t_final: float = 0.1, proposal_freqs: List[int] = None):
        self.steps = steps
        self.t_init = t_init
        self.t_final = t_final
        self.proposal_freqs = proposal_freqs  # optional: not used in this minimal version

    def _compute_oracles(self, sequences: Dict[str, str], oracles: List) -> Dict:
        # Accumulate outputs into a single dict of dicts; later terms can read them.
        outputs = {}
        for o in oracles:
            out = o.compute(sequences)
            # merge dicts shallowly
            for k, v in out.items():
                if k not in outputs:
                    outputs[k] = v
                else:
                    # If duplicate keys, last writer wins for simplicity
                    outputs[k] = v
        return outputs

    def _energy(self, oracle_outputs: Dict, energy_terms: List, system_state: Dict) -> float:
        return sum(term.evaluate(oracle_outputs, system_state) for term in energy_terms)

    def _temperature(self, step: int) -> float:
        if self.steps <= 1:
            return self.t_final
        # linear schedule
        return self.t_init + (self.t_final - self.t_init) * (step / (self.steps - 1))

    def run(self, system: Dict) -> Dict:
        sequences = deepcopy(system["sequences"])
        oracles = system["oracles"]
        muts = system["mutation_protocols"]
        terms = system["energy_terms"]

        # Initial evaluation
        oracle_outputs = self._compute_oracles(sequences, oracles)
        state = {"sequences": sequences}
        energy = self._energy(oracle_outputs, terms, state)

        best = {"sequences": deepcopy(sequences), "energy": energy, "step": 0}

        for step in range(1, self.steps + 1):
            T = self._temperature(step)

            # pick one mutator uniformly
            mut = random.choice(muts)
            proposal = mut.propose(sequences, oracle_outputs)

            # evaluate new state
            oracle_outputs_new = self._compute_oracles(proposal, oracles)
            state_new = {"sequences": proposal}
            energy_new = self._energy(oracle_outputs_new, terms, state_new)

            dE = energy_new - energy
            accept = dE <= 0 or random.random() < math.exp(-dE / max(T, 1e-8))

            if accept:
                sequences = proposal
                oracle_outputs = oracle_outputs_new
                energy = energy_new

                if energy < best["energy"]:
                    best = {"sequences": deepcopy(sequences), "energy": energy, "step": step}

        return {
            "best_sequences": best["sequences"],
            "best_energy": best["energy"],
            "best_step": best["step"],
            "final_sequences": sequences,
            "final_energy": energy,
        }
