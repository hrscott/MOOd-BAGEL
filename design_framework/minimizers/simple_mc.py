from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from design_framework.core.base import Minimizer, Oracle, MutationProtocol, EnergyTerm


@dataclass
class SimpleMinimizer(Minimizer):
    """
    Minimal Monte Carlo + linear annealing minimizer.

    Expects a `system` dict with keys:
      - "sequences": Dict[str, str]
      - "oracles": List[Oracle]
      - "mutation_protocols": List[MutationProtocol]
      - "energy_terms": List[EnergyTerm]

    Parameters
    ----------
    steps:
        Number of MC steps.
    t_init:
        Initial (high) temperature.
    t_final:
        Final (low) temperature.
    proposal_freqs:
        Optional list of integer frequencies, same length as mutation_protocols.
        Controls how often each mutator is chosen. If None, choose uniformly.
    """

    steps: int = 500
    t_init: float = 1.0
    t_final: float = 0.1
    proposal_freqs: Optional[List[int]] = None

    # internal fields (not passed from config)
    _temperatures: List[float] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.steps <= 0:
            raise ValueError("steps must be positive")
        # Precompute linear schedule
        if self.steps == 1:
            self._temperatures = [self.t_final]
        else:
            self._temperatures = [
                self.t_init + (self.t_final - self.t_init) * (i / (self.steps - 1))
                for i in range(self.steps)
            ]

    def _evaluate_oracles(self, sequences: Dict[str, str], oracles: List[Oracle]) -> Dict[str, Any]:
        """Run all oracles and merge their outputs into a single dict."""
        outputs: Dict[str, Any] = {}
        for oracle in oracles:
            out = oracle.compute(sequences)
            if not isinstance(out, dict):
                raise ValueError(f"Oracle {oracle} returned non-dict output: {type(out)}")
            # later oracles can overwrite keys if necessary
            outputs.update(out)
        return outputs

    def _evaluate_energy(self, oracle_outputs: Dict[str, Any], energy_terms: List[EnergyTerm], system_state: Dict[str, Any]) -> float:
        energy = 0.0
        for term in energy_terms:
            e = term.evaluate(oracle_outputs, system_state)
            energy += float(e)
        return energy

    def _choose_mutator(self, mutators: List[MutationProtocol]) -> MutationProtocol:
        if not mutators:
            raise ValueError("No mutation protocols provided")
        if self.proposal_freqs is None:
            return random.choice(mutators)
        if len(self.proposal_freqs) != len(mutators):
            raise ValueError("proposal_freqs length must match number of mutation protocols")
        # Weighted choice
        total = sum(self.proposal_freqs)
        r = random.uniform(0, total)
        acc = 0.0
        for freq, mut in zip(self.proposal_freqs, mutators):
            acc += freq
            if r <= acc:
                return mut
        # Fallback (numerical edge)
        return mutators[-1]

    def run(self, system: Dict[str, Any]) -> Dict[str, Any]:
        # Unpack system
        sequences: Dict[str, str] = dict(system.get("sequences", {}))
        oracles: List[Oracle] = list(system.get("oracles", []))
        mutators: List[MutationProtocol] = list(system.get("mutation_protocols", []))
        energy_terms: List[EnergyTerm] = list(system.get("energy_terms", []))

        if not sequences:
            raise ValueError("System must contain non-empty 'sequences'")

        # Initial evaluation
        oracle_outputs = self._evaluate_oracles(sequences, oracles)
        energy = self._evaluate_energy(oracle_outputs, energy_terms, {"sequences": sequences})

        best = {
            "sequences": dict(sequences),
            "energy": energy,
            "step": 0,
        }

        for step in range(self.steps):
            T = self._temperatures[step]
            mut = self._choose_mutator(mutators)

            # Propose new sequences
            proposed_sequences = mut.propose(sequences, oracle_outputs)

            # Re-evaluate oracles and energy for proposal
            proposed_oracle_outputs = self._evaluate_oracles(proposed_sequences, oracles)
            proposed_energy = self._evaluate_energy(
                proposed_oracle_outputs, energy_terms, {"sequences": proposed_sequences}
            )

            dE = proposed_energy - energy
            accept = False
            if dE <= 0:
                accept = True
            else:
                if T <= 0:
                    accept = False
                else:
                    p = math.exp(-dE / T)
                    if random.random() < p:
                        accept = True

            if accept:
                sequences = proposed_sequences
                oracle_outputs = proposed_oracle_outputs
                energy = proposed_energy

                if energy < best["energy"]:
                    best["energy"] = energy
                    best["sequences"] = dict(sequences)
                    best["step"] = step + 1

        return {
            "best_sequences": best["sequences"],
            "best_energy": best["energy"],
            "best_step": best["step"],
            "final_sequences": sequences,
            "final_energy": energy,
        }
