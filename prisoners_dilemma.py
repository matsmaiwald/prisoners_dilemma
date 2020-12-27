import json
from pydantic import BaseModel
from typing import Optional, Dict
from policies import PDPolicy
from importlib import import_module


class Player:
    policy: PDPolicy
    score: float

    def __init__(self, policy: callable):
        self.policy = policy
        self.score = 0

    def get_action(self, last_move_opponent: str):
        return self.policy.action(last_move_opponent=last_move_opponent)


class PayoffMatrix:
    reward_mapping: dict

    def __init__(self):
        self.reward_mapping = {
            "coop_coop": [-1, -1],
            "coop_defect": [-3, 0],
            "defect_coop": [0, -3],
            "defect_defect": [-2, -2],
        }

    def get_payoffs(self, action_player_1: str, action_player_2: str) -> list:
        actions = f"{action_player_1}_{action_player_2}"
        payoffs = self.reward_mapping[actions]
        return {"player_1": payoffs[0], "player_2": payoffs[1]}


class Game:
    player_1: Player
    player_2: Player
    payoff_matrix: PayoffMatrix
    previous_actions = dict()

    def __init__(self):
        self.previous_actions = {"player_1": "coop", "player_2": "coop"}

    def play_round(self):
        action_player_1 = self.player_1.get_action(
            last_move_opponent=self.previous_actions["player_2"]
        )
        action_player_2 = self.player_2.get_action(
            last_move_opponent=self.previous_actions["player_1"]
        )
        self.previous_actions = {
            "player_1": action_player_1,
            "player_2": action_player_2,
        }
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
    policy_player_1: str
    policy_player_1_kwargs: Optional[Dict[str, float]]
    policy_player_2: str
    policy_player_2_kwargs: Optional[Dict[str, float]]


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path")
    args = parser.parse_args()

    with open(args.config_path) as f:
        config_raw = json.load(f)
    config = PDConfig(**config_raw)
    my_game = Game()

    policies_module = import_module("policies")
    player_1_policy = getattr(policies_module, config.policy_player_1)
    player_2_policy = getattr(policies_module, config.policy_player_2)

    my_game.player_1 = Player(policy=player_1_policy(**config.policy_player_1_kwargs))
    my_game.player_2 = Player(policy=player_2_policy(**config.policy_player_2_kwargs))

    my_game.payoff_matrix = PayoffMatrix()

    for i in range(1, 10000):
        my_game.play_round()


if __name__ == "__main__":
    main()
