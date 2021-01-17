import json
from pydantic import BaseModel
from typing import Optional, Dict
from policies import PDPolicy
from importlib import import_module
from typing import List, Union


class Player:
    """Basic player class, has policy and score."""

    policy: PDPolicy
    score: float

    def __init__(self, policy: callable):
        self.policy = policy
        self.score = 0

    def get_action(self, last_moves_opponent: List[str]):
        """Get action from policy."""
        return self.policy.get_action(last_moves_opponent=last_moves_opponent)


class PayoffMatrix:
    """Responsible for calculating payoffs."""

    reward_mapping: dict

    def __init__(self):
        self.reward_mapping = {
            "coop_coop": [-1, -1],
            "coop_defect": [-3, 0],
            "defect_coop": [0, -3],
            "defect_defect": [-2, -2],
        }

    def get_payoffs(self, action_player_1: str, action_player_2: str) -> list:
        """Return both players' payoffs."""
        actions = f"{action_player_1}_{action_player_2}"
        payoffs = self.reward_mapping[actions]
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
        self.player_1.score += payoffs["player_1"]
        self.player_2.score += payoffs["player_2"]

        print(f"Player 1 plays: {action_player_1}")
        print(f"Player 2 plays: {action_player_2}")
        print(f"This round's payoffs are: {payoffs}")
        print(
            f"The cumulative payoffs are: [{self.player_1.score}, {self.player_2.score}]"
        )


class PDConfig(BaseModel):
    """Configuration for policies to be used by players."""

    policy_player_1: str
    policy_player_1_kwargs: Optional[Dict[str, Union[float, int]]]
    policy_player_2: str
    policy_player_2_kwargs: Optional[Dict[str, Union[float, int]]]
    n_rounds: int


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path")
    args = parser.parse_args()

    config = PDConfig.parse_file(args.config_path)

    policies_module = import_module("policies")
    player_1_policy = getattr(policies_module, config.policy_player_1)
    player_2_policy = getattr(policies_module, config.policy_player_2)

    player_1 = Player(policy=player_1_policy(**config.policy_player_1_kwargs))
    player_2 = Player(policy=player_2_policy(**config.policy_player_2_kwargs))

    payoff_matrix = PayoffMatrix()
    my_game = Game(players=[player_1, player_2], payoff_matrix=payoff_matrix)

    for i in range(1, config.n_rounds):
        my_game.play_round()


if __name__ == "__main__":
    main()
