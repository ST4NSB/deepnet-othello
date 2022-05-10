import re
import csv

class Helpers:

    @staticmethod
    def find_game_details(inputtext, game_keyword='server_game.initializeServerGame'):
        match = re.search(rf'[^>]*{game_keyword}[^;]*', inputtext)
        if match:
            return match.group(0)

    @staticmethod
    def get_first_number(str):
        return int(re.search('[0-9]+', str).group())

    @staticmethod
    def convert_list_moves_to_string_moves(move_list):
        seq = ''
        for item in move_list:
            seq += item
        return seq

    @staticmethod
    def get_games_from_dataset(location):
        rows = []
        with open(location, 'r') as file:
            reader = csv.reader(file)
            for r in reader:
                rows.append(r)
        return rows