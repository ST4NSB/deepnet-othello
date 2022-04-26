from game import Game
from logger import Logger
import config

def main():
    logger = Logger()
    
    game = Game(logger)
    game.init_game(config.settings['color'], config.settings['bot_level'])

if __name__ == "__main__":
    main()