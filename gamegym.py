import requests
from boardlogic import BoardLogic
from helpers import *
from coder import *
import os
from dotenv import load_dotenv
import json
import matplotlib.pyplot as plt

# creates the game interface on www.othello.com
class GameGym:
    def __init__(self, logger, predictor, debug = False):
        load_dotenv()
        self.__cookie = os.getenv('COOKIE')
        self.logger = logger
        self.predictor = predictor
        self.debug = debug

    def init_game(self, color, bot_level):
        # init
        self.board_logic = BoardLogic(color)

        # create game
        game_id = self.create_game_id(color, bot_level)

        # game logic
        turn, moves, winner = self.get_game_details(game_id, look_for_moves=False)
        self.board_logic.sequence = Helpers.convert_list_moves_to_string_moves(moves)
        self.board_logic.move_sequence_to_board()
        while turn != 'finished':
            encoded_move = self.calculate_move(game_id, color, turn)
            turn, moves, winner = self.get_game_details(game_id, look_for_moves=True)

            self.board_logic.sequence += encoded_move
            new_sequence = Helpers.convert_list_moves_to_string_moves(moves)
            if len(new_sequence) >= len(self.board_logic.sequence):
                self.board_logic.sequence = new_sequence
            else:
                break
            self.board_logic.move_index = len(self.board_logic.sequence) // 2 + 1
            self.board_logic.move_sequence_to_board()

        if self.debug:
            b, w = self.board_logic.get_scorepoints()
            self.logger.log_info(f'move index: {self.board_logic.move_index - 1}')
            self.logger.log_info(f'black score: {b}, white score: {w}')
            self.logger.log_board(self.board_logic.board, self.board_logic.BOARD_SIZE)

        if not winner:
            b, w = self.board_logic.get_scorepoints()
            r = b - w
            if r > 0:
                winner = 'black'
            elif r < 0:
                winner = 'white'
            else: 
                winner = 'draw'

        return (self.board_logic.sequence, winner)    

    def calculate_move(self, game_id, color, turn):
        valid_moves = self.board_logic.get_valid_moves(color)
        if len(valid_moves) == 0:
            return

        if self.debug:
            encoded_moves = []
            for move in valid_moves:
                encoded_moves.append(Coder.encode_move(move[0], move[1]))
            self.logger.log_info(f'move index: {self.board_logic.move_index}')
            self.logger.log_info(f'valid moves indexs: {valid_moves}')
            self.logger.log_info(f'valid moves: {encoded_moves}')
            b, w = self.board_logic.get_scorepoints()
            self.logger.log_info(f'black score: {b}, white score: {w}')
            self.logger.log_board(self.board_logic.board, self.board_logic.BOARD_SIZE)

        coord_move = list(valid_moves)[-1]
        if len(valid_moves) > 1:
            coord_move = self.predictor.predict_move(self.board_logic.board, valid_moves)

        encoded_move = Coder.encode_move(coord_move[0], coord_move[1])

        self.make_move(game_id, encoded_move)
        return encoded_move
        # self.board_logic.move_index += 1
        # self.board_logic.move_sequence_to_board()

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

        if self.debug:
            self.logger.log_info(f'{game_id}, {type(game_id)}')
        return game_id

    def get_game_details(self, game_id, look_for_moves):
        url = "https://www.eothello.com/get-game-updates"

        payload = f"game_id={game_id}&last_board_moves={self.board_logic.sequence}&last_chat_message_id=-1"
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
        result = json.loads(json.loads(response.text)['content'])
        if 'moves' not in result and look_for_moves:
            raise ValueError('moves is not found in result.')
        return (result['turn'], [] if 'moves' not in result else result['moves'], result['winner'])

    def make_move(self, game_id, move):
        url = "https://www.eothello.com/make-move"

        payload = f"game_id={game_id}&move={move}&move_index={self.board_logic.move_index}"
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
        if self.debug:
            self.logger.log_info(f'Make move response code: {response.status_code}')
            
    
        