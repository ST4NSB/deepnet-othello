from gamegym import GameGym
from logger import Logger
import config
from predictor import Predictor
import matplotlib.pyplot as plt
from agent import Agent

if __name__ == "__main__":
    logger = Logger()
    predictor = Predictor()
    agent = 0 #Agent(gamma=0.9, states=[], policy=None, randomFactor=0.2)
    
    wins = 0
    acc = 0
    total_reward_history = []
    win_history = []
    
    for nr in range(config.settings['number_of_games']):
        env = GameGym(logger, predictor, agent, debug=config.settings['showDebug'])
        seq, winner, reward_history = env.init_game(config.settings['color'], config.settings['bot_level'])
        total_reward_history.extend((reward_history))

        logger.log_info(f"Game {nr+1} done!")
        logger.log_info(f"Winner is: {winner}, Game sequence: {seq}")
        
        if winner == config.settings['color']:
            wins += 1
        win_history.append(wins)

    plt.plot(total_reward_history)
    plt.show()

    plt.plot(win_history)
    plt.show()

    acc = wins / config.settings['number_of_games']
    logger.log_info(f'Accuracy: {acc}')
