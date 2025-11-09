from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Sequence

import numpy as np

from design_framework.core.base import Oracle


@dataclass
class ColabDesignFoldingOracle(Oracle):
    """
    Folding oracle backed by ColabDesign's AlphaFold wrapper.

    This class is intended to run INSIDE the ColabDesign GPU environment
    (e.g. the Docker image under `infra/gpu/docker`), where:
      - `colabdesign` is installed
      - AlphaFold params are available
      - JAX is configured with GPU support

    Contract:
      - Input:  chains: Dict[str, str]   (chain_name -> AA sequence)
      - Output: dict with keys
          - 'pLDDT': Dict[str, float]   # per-chain mean pLDDT in [0, 1]
          - 'pTM': float                # scalar pTM in [0, 1]
          - 'PAE': np.ndarray | None    # (L, L) matrix or None

    Notes
    -----
    * This implementation focuses on getting pLDDT and pTM out of ColabDesign.
    * It treats the complex as a single multichain sequence, separated by ':'.
      This mirrors how ColabDesign / ColabFold handle complexes.
    * PAE support is left as an optional enhancement; many simple scoring
      schemes only need pLDDT and pTM.
    """

    num_models: int = 1
    num_recycles: int = 1
    model_name: str = "af2"
    random_seed: Optional[int] = None

    # internal AF model (lazily initialised)
    _af_model: Any = field(init=False, repr=False, default=None)

    def _lazy_init_model(self) -> None:
        """Initialise the ColabDesign AF model on first use."""
        if self._af_model is not None:
            return

        try:
            # ColabDesign >= v1.1 typically exposes mk_af_model at top level
            from colabdesign import mk_af_model  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "ColabDesignFoldingOracle requires the 'colabdesign' package "
                "and a properly configured AlphaFold environment. "
                "Make sure you are running inside the ColabDesign Docker "
                "or a compatible environment."
            ) from exc

        # mk_af_model() defaults are usually fine; model_name kept for future use
        self._af_model = mk_af_model()

    def _build_complex_sequence(self, chains: Dict[str, str]) -> str:
        """
        Join multiple chains into a single multi-chain sequence string.

        ColabDesign / AF typically interpret ':' as a chain separator.
        The order is deterministic: sorted by chain name.
        """
        # stable order of chains
        items: Sequence[tuple[str, str]] = sorted(chains.items(), key=lambda kv: kv[0])
        return ":".join(seq for _, seq in items)

    def compute(self, chains: Dict[str, str]) -> Dict[str, Any]:
        """
        Run AlphaFold via ColabDesign on the provided chains.

        Parameters
        ----------
        chains:
            Mapping chain_name -> amino-acid sequence.

        Returns
        -------
        dict with 'pLDDT', 'pTM', 'PAE' as described in the class docstring.
        """
        if not chains:
            raise ValueError("ColabDesignFoldingOracle.compute() received no chains")

        self._lazy_init_model()
        assert self._af_model is not None

        seq_complex = self._build_complex_sequence(chains)

        # ColabDesign AF model typically exposes a .predict(...) method that
        # fills `af_model.aux["log"]` with metrics including 'ptm' and 'plddt'.
        # See e.g. "ProteinMPNN in Jax!" examples.
        #
        # We call it in a minimal configuration here.
        self._af_model.predict(
            seq=seq_complex,
            num_recycles=self.num_recycles,
            num_models=self.num_models,
            verbose=False,
            random_seed=self.random_seed,
        )

        log = getattr(self._af_model, "aux", {}).get("log", {})

        # pTM as a scalar [0, 1]
        ptm = float(log.get("ptm", 0.0))

        # ColabDesign typically stores mean pLDDT as a percentage [0, 100]
        # We normalise to [0, 1] to match the stub oracle convention.
        raw_plddt = float(log.get("plddt", 0.0))
        mean_plddt = raw_plddt / 100.0 if raw_plddt > 1.0 else raw_plddt

        # For now, assign the same mean pLDDT to all chains; finer-grained
        # per-chain scores can be added later by inspecting per-residue arrays.
        plddt_per_chain: Dict[str, float] = {name: mean_plddt for name in chains.keys()}

        # PAE: left as None for now; can be filled in once we decide how to
        # decode it from the AF model outputs in this environment.
        pae: Optional[np.ndarray] = None

        return {
            "pLDDT": plddt_per_chain,
            "pTM": ptm,
            "PAE": pae,
        }
