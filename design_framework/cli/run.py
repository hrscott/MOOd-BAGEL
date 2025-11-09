import argparse
import importlib
from pathlib import Path
from typing import Any, Dict, List

import yaml

from design_framework.core.base import Oracle, EnergyTerm, MutationProtocol, Minimizer


def _instantiate_from_config(obj_cfg: Dict[str, Any]) -> Any:
    """
    Instantiate an object from a simple config dict:

    {
      "module": "design_framework.oracles.folding_oracle",
      "class": "FoldingOracle",
      "params": { ... }
    }
    """
    module_name = obj_cfg["module"]
    cls_name = obj_cfg["class"]
    params = obj_cfg.get("params", {}) or {}

    module = importlib.import_module(module_name)
    cls = getattr(module, cls_name)
    return cls(**params)


def load_config(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError(f"Top-level YAML structure must be a mapping, got {type(cfg)}")
    return cfg


def build_system_from_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    # Initial sequences: {chain_name: "SEQ"}
    sequences: Dict[str, str] = cfg.get("initial_sequences", {})
    if not sequences:
        raise ValueError("Config must define 'initial_sequences' as a mapping of chain_name -> sequence")

    # Oracles
    oracle_cfgs: List[Dict[str, Any]] = cfg.get("oracles", [])
    oracles: List[Oracle] = []
    for oc in oracle_cfgs:
        oracles.append(_instantiate_from_config(oc))

    # Mutation protocols
    mut_cfgs: List[Dict[str, Any]] = cfg.get("mutation_protocols", [])
    mutators: List[MutationProtocol] = []
    for mc in mut_cfgs:
        mutators.append(_instantiate_from_config(mc))

    # Energy terms
    energy_cfgs: List[Dict[str, Any]] = cfg.get("energy_terms", [])
    energy_terms: List[EnergyTerm] = []
    for ec in energy_cfgs:
        energy_terms.append(_instantiate_from_config(ec))

    # Minimizer (exactly one)
    minimizer_cfg = cfg.get("minimizer")
    if minimizer_cfg is None:
        raise ValueError("Config must define a 'minimizer' section")
    minimizer: Minimizer = _instantiate_from_config(minimizer_cfg)

    system: Dict[str, Any] = {
        "sequences": sequences,
        "oracles": oracles,
        "mutation_protocols": mutators,
        "energy_terms": energy_terms,
    }

    return system, minimizer


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a simple design_framework MC optimization from a YAML config.")
    parser.add_argument(
        "config",
        type=str,
        help="Path to YAML config file describing initial sequences, oracles, mutation protocols, energy terms, and minimizer.",
    )
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    system, minimizer = build_system_from_config(cfg)

    result = minimizer.run(system)

    print("=== RESULT ===")
    print(f"Best energy: {result.get('best_energy')}")
    print(f"Best step:   {result.get('best_step')}")
    print("Best sequences:")
    best_seqs = result.get("best_sequences", {})
    for name, seq in best_seqs.items():
        print(f"  {name}: {seq}")


if __name__ == "__main__":
    main()
