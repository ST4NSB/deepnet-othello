from game import Game
from logger import Logger
import config
from predictor import Predictor

def main():
    logger = Logger()
    predictor = Predictor()
    
    game = Game(logger, predictor)
    seq, winner = game.init_game(config.settings['color'], config.settings['bot_level'])

    print(f"\n\nWinner is: {winner}, Game sequence: {seq}")

if __name__ == "__main__":
    main()