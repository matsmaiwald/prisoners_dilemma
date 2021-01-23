from abc import ABC
from typing import Dict, List
import itertools

import random


class PDPolicy(ABC):
    """Base class defining interface of all policies."""

    def get_action(self, last_moves_opponent: List[str]):
        """Return action as response to opponent's last moves."""
        raise NotImplementedError


class AlwaysCoopPolicy(PDPolicy):
    """Will always cooperate."""

    def get_action(self, last_moves_opponent: List[str]):
        return "coop"


class AlwaysDefectPolicy(PDPolicy):
    """Will always defect."""

    def get_action(self, last_moves_opponent: List[str]):
        return "defect"


class ProbabilisticPolicy(PDPolicy):
    """test docstring"""

    p_defect: float

    def __init__(self, p_defect: float):
        self.p_defect = p_defect

    def get_action(self, last_moves_opponent: List[str]):
        return "defect" if random.random() < self.p_defect else "coop"


class TitForTatPolicy(PDPolicy):
    """Defect if opponent defected last turn, cooperate otherwise."""

    def get_action(self, last_moves_opponent: List[str]):
        if last_moves_opponent == []:
            return "coop"
        else:
            return "defect" if last_moves_opponent[-1] == "defect" else "coop"


class RandomStaticPolicy(PDPolicy):
    """
    General random static policy class.

    Note: For ease of implementation, coop: 1, defec: 0.
    """

    length_lookback: int
    _action_mapping: Dict[str, int]

    def __init__(self, length_lookback: int):
        self.length_lookback = int(length_lookback)
        self._initialise_random()

    def _initialise_random(self):
        """Initialise policy to random mapping."""
        keys = [
            "".join(seq) for seq in itertools.product("01", repeat=self.length_lookback)
        ]
        values = [str(random.randint(0, 1)) for i in range(len(keys))]
        self._action_mapping = dict(zip(keys, values))

    def _decode_action(self, action: str) -> str:
        mapping = {"coop": "1", "defect": "0"}
        return mapping[action]

    def _encode_action(self, action: str) -> str:
        mapping = {"1": "coop", "0": "defect"}
        return mapping[action]

    def _handle_missing_history(
        self, last_moves_opponent: List[str], replacement_value: str
    ) -> List[str]:
        """In case number of rounds played is smaller than lookback length,
        assume that opponent cooperated in the missing rounds."""
        n_missing_entries = self.length_lookback - len(last_moves_opponent)
        for i in range(n_missing_entries):
            last_moves_opponent.insert(0, "coop")
        return last_moves_opponent

    def get_action(self, last_moves_opponent: List[str]) -> str:
        """Get action, given the past moves of the opponent."""
        if len(last_moves_opponent) < self.length_lookback:
            self._handle_missing_history(
                last_moves_opponent=last_moves_opponent, replacement_value="coop"
            )
        # filter to lookback length
        last_moves_opponent_relevant = last_moves_opponent[
            -self.length_lookback :  # noqa: E203
        ]
        last_moves_opponent_decoded = list(
            map(self._decode_action, last_moves_opponent_relevant)
        )
        action_decoded = self._action_mapping["".join(last_moves_opponent_decoded)]

        return self._encode_action(action_decoded)

