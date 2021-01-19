import json
from pydantic import BaseModel
from typing import Optional, Dict
from policies import PDPolicy
from importlib import import_module
from typing import List, Union
import random


class Player:
    """Basic player class, has policy and score."""

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

    reward_mapping: dict

    def __init__(self):
        self.reward_mapping = {
            "coop_coop": [4, 4],
            "coop_defect": [-3, 5],
            "defect_coop": [5, -3],
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
        self.player_1.score += payoffs["player_1"] + random.uniform(-1e-10, 1e-10)
        self.player_2.score += payoffs["player_2"] + random.uniform(-1e-10, 1e-10)

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


def create_player(policy_name: str, policy_kwargs: dict) -> Player:

    policies_module = import_module("policies")
    policy_class = getattr(policies_module, policy_name)

    player = Player(policy=policy_class(**policy_kwargs))
    return player


def main_ko():
    # import argparse

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--config_path")
    # args = parser.parse_args()

    # config = PDConfig.parse_file(args.config_path)
    n_players = 1024
    n_rounds = 50
    length_lookback = 2
    players = list()
    for i in range(0, n_players):
        player = create_player(
            "GeneralPolicy", policy_kwargs={"length_lookback": length_lookback}
        )
        players.append(player)

    payoff_matrix = PayoffMatrix()

    k = 0
    while k < n_players // 2 and len(players) > 1:
        j = 0
        while j < len(players) - 1:

            my_game = Game(
                players=[players[j], players[j + 1]], payoff_matrix=payoff_matrix
            )

            for i in range(1, n_rounds):
                my_game.play_round()
            if players[j].score < players[j + 1].score:
                players[j + 1].score = 0
                players.pop(j)
            else:
                players[j].score = 0
                players.pop(j + 1)
    print("The tournament is over!")
    print("The winning player's strategy is:")
    print(players[0].policy._action_mapping)


class TournamnetConfig(BaseModel):
    n_players: int
    n_rounds: int
    length_lookback: int
    payoff_matrix: PayoffMatrix

    class Config:
        arbitrary_types_allowed = True


class EvolutionTournament:
    config: TournamnetConfig
    players: List[Player]

    def __init__(self, config: TournamnetConfig):
        self.config = config
        self._initialise()

    def _get_average_score(self):
        cum_sum = 0
        for player in self.players:
            cum_sum += player.score
        return cum_sum / len(self.players)

    def _initialise(self):
        self.players = []
        for i in range(0, self.config.n_players):
            player = create_player(
                "GeneralPolicy",
                policy_kwargs={"length_lookback": self.config.length_lookback},
            )
            self.players.append(player)

    def _run_match(self, player_1: Player, player_2: Player):
        my_game = Game(
            players=[player_1, player_2], payoff_matrix=self.config.payoff_matrix,
        )

        for i in range(1, self.config.n_rounds):
            my_game.play_round()

    def _run_stage(self):
        j = 0
        while j < len(self.players) - 1:
            self._run_match(player_1=self.players[j], player_2=self.players[j + 1])

            j = j + 2
        average_score = self._get_average_score()
        if len(self.players) > 1:
            print(f"Number of players still in game: {len(self.players)}")
            self.players = [
                player for player in self.players if player.score > average_score
            ]

    def run_tournament(self):
        k = 0
        while k < self.config.n_players // 2 and len(self.players) > 1:
            self._run_stage()
        print("The tournament is over!")
        print("The winning player's strategy is:")
        print(self.players[0].policy._action_mapping)


def main_survival():
    # config = PDConfig.parse_file(args.config_path)
    n_players = 512
    n_rounds = 50
    length_lookback = 2
    payoff_matrix = PayoffMatrix()

    torunament_config = TournamnetConfig(
        n_players=n_players,
        n_rounds=n_rounds,
        length_lookback=length_lookback,
        payoff_matrix=payoff_matrix,
    )
    tournament = EvolutionTournament(config=torunament_config)
    tournament.run_tournament()


if __name__ == "__main__":
    main_survival()
