from game import Game
from logger import Logger

def main():
    logger = Logger()
    game = Game(logger)

    game.create_game("black", 1)
    

if __name__ == "__main__":
    main()