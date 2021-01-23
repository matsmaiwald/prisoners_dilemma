from pydantic import BaseModel
from importlib import import_module
from typing import List, Dict
from game import Player, PayoffMatrix, Game


def create_player(policy_name: str, policy_kwargs: dict) -> Player:

    policies_module = import_module("policies")
    policy_class = getattr(policies_module, policy_name)

    player = Player(policy=policy_class(**policy_kwargs))
    return player


class TournamentConfig(BaseModel):
    n_players: int
    n_rounds: int
    length_lookback: int
    payoff_mapping: Dict[str, List[float]]


class EvolutionTournament:
    config: TournamentConfig
    payoff_matrix: PayoffMatrix
    players: List[Player]

    def __init__(self, config: TournamentConfig):
        self.config = config
        self._initialise()
        self.payoff_matrix = PayoffMatrix(payoff_mapping=config.payoff_mapping)

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
        my_game = Game(players=[player_1, player_2], payoff_matrix=self.payoff_matrix,)

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

