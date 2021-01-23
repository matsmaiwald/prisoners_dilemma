"""Module with classes necessary to play a (repeated) prisoners' dilemma."""
from policies import PDPolicy
from typing import List
import random


class Player:
    """Player class, has policy and keeps score."""

    policy: PDPolicy
    score: float
    is_active: bool

    def __init__(self, policy: callable):
        self.policy = policy
        self.score = 0
        self.is_active = True

    def get_action(self, last_moves_opponent: List[str]):
        """Get action from policy."""
        return self.policy.get_action(last_moves_opponent=last_moves_opponent)


class PayoffMatrix:
    """Responsible for calculating payoffs."""

    payoff_mapping: dict

    def __init__(self, payoff_mapping):
        self.payoff_mapping = payoff_mapping

    def get_payoffs(self, action_player_1: str, action_player_2: str) -> list:
        """Return both players' payoffs."""
        actions = f"{action_player_1}_{action_player_2}"
        payoffs = self.payoff_mapping[actions]
        return {"player_1": payoffs[0], "player_2": payoffs[1]}


class Game:
    """Game class, has two players, payoff matrix and history of moves."""

    player_1: Player
    player_2: Player
    payoff_matrix: PayoffMatrix
    previous_actions = dict()

    def __init__(self, players: List[Player], payoff_matrix: PayoffMatrix):
        self.player_1 = players[0]
        self.player_2 = players[1]
        self.payoff_matrix = payoff_matrix
        self.previous_actions = {"player_1": [], "player_2": []}

    def play_round(self):
        """Play a round of prisoner's dilemma."""
        action_player_1 = self.player_1.get_action(
            last_moves_opponent=self.previous_actions["player_2"]
        )
        action_player_2 = self.player_2.get_action(
            last_moves_opponent=self.previous_actions["player_1"]
        )
        self.previous_actions["player_1"].append(action_player_1)
        self.previous_actions["player_2"].append(action_player_2)

        payoffs = self.payoff_matrix.get_payoffs(action_player_1, action_player_2)
        self.player_1.score += payoffs["player_1"] + random.uniform(-1e-10, 1e-10)
        self.player_2.score += payoffs["player_2"] + random.uniform(-1e-10, 1e-10)

        print(f"Player 1 plays: {action_player_1}")
        print(f"Player 2 plays: {action_player_2}")
        print(f"This round's payoffs are: {payoffs}")
        print(
            f"The cumulative payoffs are: [{self.player_1.score}, {self.player_2.score}]"
        )

