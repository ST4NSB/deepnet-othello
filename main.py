from game import Game
from logger import Logger
import config
from predictor import Predictor

def main():
    logger = Logger()
    predictor = Predictor()
    
    game = Game(logger, predictor)
    game.init_game(config.settings['color'], config.settings['bot_level'])

if __name__ == "__main__":
    main()