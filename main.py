from evolution_tournament import TournamentConfig, EvolutionTournament


def main():
    tournament_config = TournamentConfig.parse_file("./tournament_config.json")
    tournament = EvolutionTournament(config=tournament_config)
    tournament.run_tournament()


if __name__ == "__main__":
    main()
