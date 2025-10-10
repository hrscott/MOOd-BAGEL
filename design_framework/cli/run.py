import yaml
from importlib import import_module


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _instantiate(obj_cfg):
    module = obj_cfg["module"]
    cls = obj_cfg["class"]
    params = obj_cfg.get("params", {})
    mod = import_module(module)
    return getattr(mod, cls)(**params)


def run_from_config(config_path: str):
    cfg = load_config(config_path)
    sequences = cfg["initial_sequences"]

    # instantiate oracles
    oracles = [_instantiate(o) for o in cfg.get("oracles", [])]

    # instantiate mutation protocols
    muts = [_instantiate(m) for m in cfg.get("mutation_protocols", [])]

    # instantiate energy terms
    terms = [_instantiate(e) for e in cfg.get("energy_terms", [])]

    # instantiate minimizer
    minimizer = _instantiate(cfg["minimizer"])

    system = {
        "sequences": sequences,
        "oracles": oracles,
        "mutation_protocols": muts,
        "energy_terms": terms,
    }
    result = minimizer.run(system)
    print("=== RESULT ===")
    print(result)
    return result


if __name__ == "__main__":
    import sys
    run_from_config(sys.argv[1])
