from abc import ABC

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
