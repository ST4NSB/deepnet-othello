import requests
from helpers import *
from coder import *
import os
from dotenv import load_dotenv
import json

# creates the game interface on www.othello.com
class Game:

    def __init__(self, logger):
        load_dotenv()
        self.__cookie = os.getenv('COOKIE')
        self.BOARD_SIZE = 8
        self.logger = logger

    def init_game(self, color, bot_level):
        # init
        self.board = self.clear_board()
        self.sequence = ''

        # create game
        # game_id = self.create_game_id(color, bot_level)

        # game logic
        # turn = self.get_game_turn(game_id)
        # while turn != 'finished':
        #     if turn != color:
        #         turn = self.get_game_turn(game_id)
        #         continue
                
            
            


            # turn = self.get_game_turn(game_id)


        #move = self.get_game_turn(1357275)
        #print(move)
        pass


    def calculate_move(self, color):
        pass
        


    def get_valid_moves(self, color):
        valid_moves = set()
        
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                pass
        

    def create_game_id(self, color, bot_level):
        bot_id = 2181 + bot_level
        url = f"https://www.eothello.com/add-challenge/{bot_id}"

        payload= f'color={color.capitalize()}&type=0&rated=no&challenge=Challenge'
        headers = {
            'authority': 'www.eothello.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'origin': 'https://www.eothello.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': f'https://www.eothello.com/create-challenge/{bot_id}',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': f'{self.__cookie}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        game_function_details = Helpers.find_game_details(response.text)
        game_id = Helpers.get_first_number(game_function_details)

        self.logger.log_info(f'{game_id}, {type(game_id)}')
        return game_id

    def get_game_turn(self, game_id):
        url = "https://www.eothello.com/get-game-updates"

        payload = f"game_id={game_id}&last_board_moves=&last_chat_message_id=-1"
        headers = {
            'authority': 'www.eothello.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://www.eothello.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.eothello.com/game/1205470',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': f'{self.__cookie}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        result = json.loads(json.loads(response.text)['content'])
        return result['turn']

    def make_move(self, game_id, move, index):
        url = "https://www.eothello.com/make-move"

        payload = f"game_id={game_id}&move={move}&move_index={index}"
        headers = {
            'authority': 'www.eothello.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://www.eothello.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': f'https://www.eothello.com/game/{game_id}',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': f'{self.__cookie}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        self.logger.log_info(f'{response.status_code}')
            
    def clear_board(self):
        board = [[Coder.encode_game_string(None) for x in range(self.BOARD_SIZE)] for x in range(self.BOARD_SIZE)]
        board[3][3] = Coder.encode_game_string('white')
        board[3][4] = Coder.encode_game_string('black')
        board[4][3] = Coder.encode_game_string('black')
        board[4][4] = Coder.encode_game_string('white')
        return board
        





