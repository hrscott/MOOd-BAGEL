from __future__ import annotations
import os, tempfile, subprocess, json, pathlib
from typing import Dict
from design_framework.core.base import Oracle

_HYDROS = set("AILMVFWY")

def _mean_bfactor_from_pdb(pdb_path: str) -> float:
    """
    Minimal PDB parser to average B-factor (columns 61-66) across ATOM rows.
    In AF/ColabFold outputs, B-factor stores pLDDT (0..100).
    """
    total, n = 0.0, 0
    with open(pdb_path, "r") as fh:
        for line in fh:
            if line.startswith("ATOM"):
                try:
                    b = float(line[60:66])
                except Exception:
                    continue
                total += b
                n += 1
    return (total / n) if n else 0.0

class FoldingOracle(Oracle):
    """
    Folding oracle with two modes:
      - backend='stub' (default): deterministic composition-based fake pLDDT in 0..1
      - backend='colabfold': run `colabfold_batch` per chain (monomer) and derive mean pLDDT from PDB B-factors.
    Notes:
      * For simplicity, we run *per chain* as monomers and average pLDDT per chain.
      * pTM and PAE are returned as 0.0 / None here; you can extend to parse result JSON/PAE if you run multimers.
    """
    def __init__(self, backend: str = "stub", models: int = 1, recycles: int = 1):
        self.backend = backend
        self.models = int(models)
        self.recycles = int(recycles)

    def compute(self, chains: Dict[str, str]) -> Dict:
        if self.backend == "stub":
            plddt = {}
            for name, seq in chains.items():
                if not seq:
                    plddt[name] = 0.0
                    continue
                frac_h = sum(aa in _HYDROS for aa in seq) / max(1, len(seq))
                plddt[name] = 0.2 + 0.7 * frac_h  # 0..1
            return {"coords": {k: None for k in chains}, "pLDDT": plddt, "PAE": None, "pTM": 0.0}

        if self.backend == "colabfold":
            # Ensure colabfold_batch exists
            if not shutil.which("colabfold_batch"):
                raise RuntimeError("colabfold_batch not found on PATH. Install ColabFold and ensure 'colabfold_batch' is available.")
            import shutil

            plddt = {}
            with tempfile.TemporaryDirectory() as work:
                work = pathlib.Path(work)
                for name, seq in chains.items():
                    # write FASTA for this chain
                    fasta = work / f"{name}.fasta"
                    with open(fasta, "w") as fh:
                        fh.write(f">{name}\n{seq}\n")

                    outdir = work / f"out_{name}"
                    outdir.mkdir(parents=True, exist_ok=True)
                    cmd = [
                        "colabfold_batch",
                        "--num-models", str(self.models),
                        "--num-recycle", str(self.recycles),
                        str(fasta), str(outdir)
                    ]
                    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    # pick the first (or top-ranked) model pdb in output dir
                    pdbs = sorted(outdir.glob("*.pdb"))
                    if not pdbs:
                        plddt[name] = 0.0
                        continue
                    mean_b = _mean_bfactor_from_pdb(str(pdbs[0]))  # pLDDT in 0..100
                    plddt[name] = max(0.0, min(1.0, mean_b / 100.0))

            return {"coords": {k: None for k in chains}, "pLDDT": plddt, "PAE": None, "pTM": 0.0}

        raise ValueError(f"Unsupported backend: {self.backend}")
