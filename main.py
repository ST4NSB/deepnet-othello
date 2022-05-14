from pydoc import Helper

from django import conf
from coder import Coder
from gamegym import GameGym
from helpers import Helpers
from logger import Logger
import config
from predictor import Predictor
import matplotlib.pyplot as plt

if __name__ == "__main__":
    logger = Logger()    
    predictor = Predictor(logger, 
                          color=config.settings['color'], 
                          location=config.settings['dataset_location'],
                          checkpoint=config.settings['checkpoint_location'], 
                          load_model=config.settings['load_model'], 
                          batch_size=config.model['batch_size'],
                          model_type=config.model['model_type'],
                          epochs=config.model['epochs'],
                          split_validation=config.model['split_validation'],
                          max_loaded_matches=config.model['max_loaded_matches'],
                          debug=config.settings['show_debug'])

    wins = 0
    draws = 0
    acc = 0
    win_history = []
    games = []
    
    for nr in range(config.settings['number_of_games']):
        env = GameGym(logger, predictor, debug=config.settings['show_debug'])
        seq, winner = env.init_game(config.settings['color'], config.settings['bot_level'])

        logger.log_info(f"Game {nr+1} done!")
        logger.log_info(f"Winner is: {winner}, Game sequence: {seq}")
        
        if winner == config.settings['color']:
            wins += 1
        elif winner != 'black' and winner != 'white':
            draws += 1
        win_history.append(wins)
        
        winner_id = '0'
        if winner == 'black':
            winner_id = '1'
        elif winner == 'white':
            winner_id = '-1'
        games.append([nr + 1, winner_id, seq])

    if config.settings['save_games']:
        Helpers.save_csv(games, config.settings['my_games_location'])

    plt.plot(win_history)
    plt.show()

    games = config.settings['number_of_games']
    losses = games - wins - draws
    logger.log_info(f'Number of games: {games}, wins: {wins}, draws: {draws}, losses: {losses}')
