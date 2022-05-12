from pydoc import Helper
from coder import Coder
from gamegym import GameGym
from helpers import Helpers
from logger import Logger
import config
from predictor import Predictor
import matplotlib.pyplot as plt

if __name__ == "__main__":
    logger = Logger()    
    predictor = Predictor(logger, color=config.settings['color'], location=config.settings['xml_location'], checkpoint=config.settings['checkpoint_location'], load_model=config.settings['load_model'], debug=config.settings['showDebug'])

    wins = 0
    draws = 0
    acc = 0
    win_history = []
    
    for nr in range(config.settings['number_of_games']):
        env = GameGym(logger, predictor, debug=config.settings['showDebug'])
        seq, winner = env.init_game(config.settings['color'], config.settings['bot_level'])

        logger.log_info(f"Game {nr+1} done!")
        logger.log_info(f"Winner is: {winner}, Game sequence: {seq}")
        
        if winner == config.settings['color']:
            wins += 1
        elif winner != 'black' and winner != 'white':
            draws += 1
        win_history.append(wins)

    plt.plot(win_history)
    plt.show()

    games = config.settings['number_of_games']
    losses = games - wins - draws
    logger.log_info(f'Number of games: {games}, wins: {wins}, draws: {draws}, losses: {losses}')
