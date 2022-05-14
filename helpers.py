import re
import csv
from shutil import move
import xml.etree.ElementTree as ET

from regex import W

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

    @staticmethod
    def normalize(value, min, max):
        lowest_value = 0.001 # 0.0000000000000001
        res = (value - min) / (max - min)
        return res if res > 0.0 else lowest_value

    @staticmethod
    def get_games_from_xml(xml_location):
        tree = ET.parse(xml_location)
        root = tree.getroot()
        rows = []
        for game in root[1].getchildren():
            winner_color =  game[1].attrib['winner']
            winner = '0'
            if winner_color == 'black':
                winner = '1'
            elif winner_color == 'white':
                winner = '-1'
            moves = game[4].text
            rows.append(["", winner, moves])

        return rows

    @staticmethod
    def save_csv(arr, location):
        with open(location, 'w', newline='') as f:
            write = csv.writer(f)
            write.writerow(['id', 'winner', 'game_moves'])
            write.writerows(arr)