import re

class Helpers:

    @staticmethod
    def find_game_details(inputtext, game_keyword='server_game.initializeServerGame'):
        match = re.search(rf'[^>]*{game_keyword}[^;]*', inputtext)
        if match:
            return match.group(0)

    @staticmethod
    def get_first_number(str):
        return int(re.search('[0-9]+', str).group())