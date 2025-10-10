import random
from typing import Dict
from design_framework.core.base import MutationProtocol

AA_ALPHABET = "ACDEFGHIKLMNPQRSTVWY"

class RandomMutator(MutationProtocol):
    """
    Randomly mutate each residue with probability p_mut.
    """
    def __init__(self, p_mut: float = 0.05, alphabet: str = AA_ALPHABET):
        self.p_mut = p_mut
        self.alphabet = alphabet

    def propose(self, sequences: Dict[str, str], oracle_outputs: dict) -> Dict[str, str]:
        new = {}
        for name, seq in sequences.items():
            s = list(seq)
            for i in range(len(s)):
                if random.random() < self.p_mut:
                    s[i] = random.choice(self.alphabet)
            new[name] = "".join(s)
        return new
