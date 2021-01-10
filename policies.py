from abc import ABC
from typing import Dict, List
import itertools

import random


class PDPolicy(ABC):
    def action(self, last_move_opponent: str):
        raise NotImplementedError


class AlwaysCoopPolicy(PDPolicy):
    def action(self, last_move_opponent: str):
        return "coop"


class AlwaysDefectPolicy(PDPolicy):
    def action(self, last_move_opponent: str):
        return "defect"


class ProbabilisticPolicy(PDPolicy):
    p_defect: float

    def __init__(self, p_defect: float):
        self.p_defect = p_defect

    def action(self, last_move_opponent: str):
        return "defect" if random.random() < self.p_defect else "coop"


class TitForTatPolicy(PDPolicy):
    def action(self, last_move_opponent: str):
        return "defect" if last_move_opponent == "defect" else "coop"


class GeneralPolicy(PDPolicy):
    """
    General Policy class.

    Note: For ease of implementation, coop: 1, defec: 0.
    """

    length_lookback: int
    _action_mapping: Dict[str, int]

    def __init__(self, length_lookback: int):
        self.length_lookback = length_lookback
        self.initialise_random()

    def initialise_random(self):
        """Initialise policy to random mapping."""
        keys = [
            "".join(seq) for seq in itertools.product("01", repeat=self.length_lookback)
        ]
        values = [1 for i in range(1, len(keys))]
        self._action_mapping = dict(zip(keys, values))

    def get_action(self, past_moves_opponent: List[int]) -> str:
        """Get action, given the past moves of the opponent."""
        past_moves_opponent_str = list(map(str, past_moves_opponent))
        return self._action_mapping["".join(past_moves_opponent_str)]


def test_general_policy():
    my_policy = GeneralPolicy(length_lookback=5)
    print(my_policy._action_mapping)
    print(my_policy.get_action([1, 1, 0, 0, 0]))


if __name__ == "__main__":
    test_general_policy()
