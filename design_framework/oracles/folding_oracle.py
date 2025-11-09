from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

import numpy as np

from design_framework.core.base import Oracle


@dataclass
class FoldingOracle(Oracle):
    """
    Minimal folding oracle abstraction.

    For now we implement only a 'stub' backend that returns random-but-plausible
    values for pLDDT, pTM and PAE so that the rest of the MC pipeline can be
    exercised end-to-end.

    Later, this class will grow additional backends, e.g.:
      - 'colabdesign' using colabdesign.af
      - 'colabfold' using the colabfold Python API

    Parameters
    ----------
    backend:
        Currently only 'stub' is supported. This keeps the config interface
        stable while we incrementally wire in real GPU-backed oracles.
    seed:
        Optional random seed for reproducible stub behaviour.
    """

    backend: Literal["stub"] = "stub"
    seed: Optional[int] = None

    # internal RNG, initialised in __post_init__
    _rng: np.random.Generator = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.backend != "stub":
            raise ValueError(
                f"Unsupported backend '{self.backend}' in FoldingOracle. "
                "Only 'stub' is implemented in this minimal version."
            )
        self._rng = np.random.default_rng(self.seed)

    def compute(self, chains: Dict[str, str]) -> Dict[str, Any]:
        """
        Compute oracle outputs for the given sequences.

        Parameters
        ----------
        chains:
            Mapping chain_name -> amino-acid sequence.

        Returns
        -------
        dict with at least:
          - 'pLDDT': Dict[str, float]   # per-chain mean pLDDT in [0, 1]
          - 'pTM': float                # scalar pTM in [0, 1]
          - 'PAE': np.ndarray           # (L, L) pairwise error matrix
        """
        if self.backend == "stub":
            return self._compute_stub(chains)

        # Future: 'colabdesign' / 'colabfold' backends live here.
        raise RuntimeError(f"Backend '{self.backend}' not implemented")

    # ------------------------------------------------------------------
    # Stub backend
    # ------------------------------------------------------------------
    def _compute_stub(self, chains: Dict[str, str]) -> Dict[str, Any]:
        # Per-chain mean pLDDT in [0.7, 0.95] (reasonably confident)
        plddt: Dict[str, float] = {}
        for name, seq in chains.items():
            _ = len(seq)  # not used yet, but kept for future extension
            plddt[name] = float(self._rng.uniform(0.7, 0.95))

        # Global pTM in [0.5, 0.9]
        ptm = float(self._rng.uniform(0.5, 0.9))

        # Simple synthetic PAE matrix over the concatenated length of all chains
        total_len = sum(len(seq) for seq in chains.values())
        if total_len == 0:
            # Degenerate, but avoid crashing
            pae = np.zeros((0, 0), dtype=float)
        else:
            pae = self._rng.uniform(1.0, 5.0, size=(total_len, total_len))
            # Lower error on the diagonal to roughly emulate "self" certainty
            diag_vals = self._rng.uniform(0.1, 1.0, size=(total_len,))
            np.fill_diagonal(pae, diag_vals)

        return {
            "pLDDT": plddt,
            "pTM": ptm,
            "PAE": pae,
        }
