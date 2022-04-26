from msilib import sequence
import requests
from helpers import *
from coder import *
import os
from dotenv import load_dotenv
import json

# creates the game interface on www.othello.com
class Game:
    def __init__(self, logger, predictor):
        load_dotenv()
        self.__cookie = os.getenv('COOKIE')
        self.BOARD_SIZE = 8
        self.logger = logger
        self.predictor = predictor

    def init_game(self, color, bot_level):
        # init
        self.board = self.clear_board()
        self.sequence = ''
        self.move_index = 2 if color == 'white' else 1

        # create game
        game_id = self.create_game_id(color, bot_level)

        # game logic
        turn, moves, winner = self.get_game_details(game_id)
        self.sequence = Helpers.convert_list_moves_to_string_moves(moves)
        self.__move_sequence_to_board(color)
        while turn != 'finished':
            if turn != color: 
                turn, moves, winner = self.get_game_details(game_id)
                self.sequence = Helpers.convert_list_moves_to_string_moves(moves)
                self.__move_sequence_to_board(color)
                continue
                
            self.calculate_move(game_id, color)

            turn, moves, winner = self.get_game_details(game_id)
            self.sequence = Helpers.convert_list_moves_to_string_moves(moves)
            self.__move_sequence_to_board(color)


        #move = self.get_game_turn(1357275)
        #print(move)
        pass

    def get_score(self):
        # to be added
        # (black: points, white: points)
        # on board impl
        pass 

    def calculate_move(self, game_id, color):
        valid_moves = self.get_valid_moves(color)
        coord_move = self.predictor.predict_randomly(valid_moves)
        
        encoded_move = Coder.encode_move(coord_move[0], coord_move[1])

        self.make_move(game_id, encoded_move)

        self.sequence += encoded_move
        self.move_index += 2
        self.board[coord_move[0]][coord_move[1]] = Coder.encode_game_string(color)

    def get_valid_moves(self, color):
        valid_moves = set()
        
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] == Coder.encode_game_string(color):
                    valid_moves.update(self.__check_disc_every_direction(color, i, j))

        return valid_moves

    def __check_disc_every_direction(self, color, i, j):
        valid_moves = set()

        for k in range(8):
            dir_y = [-1, -1, 0, 1, 1, 1, 0, -1]
            dir_x = [0, 1, 1, 1, 0, -1, -1, -1]

            found_opposite_disc, leave_searching = False, False

            while (i + dir_y[k] >= 0 and i + dir_y[k] < self.BOARD_SIZE) and (j + dir_x[k] >= 0 and j + dir_x[k] < self.BOARD_SIZE):
                new_i = i + dir_y[k]
                new_j = j + dir_x[k]

                if self.board[new_i][new_j] == Coder.encode_game_string(color):
                    leave_searching = True
                elif self.board[new_i][new_j] == Coder.encode_game_string(None):
                    if found_opposite_disc:
                        valid_moves.add((new_i, new_j))
                    leave_searching = True
                else:
                    found_opposite_disc = True
                    dir_y[k] = self.__keep_same_direction_incrementer(dir_y[k])
                    dir_x[k] = self.__keep_same_direction_incrementer(dir_x[k])

                if leave_searching:
                    break

        return valid_moves

    def __keep_same_direction_incrementer(self, inc):
        if inc > 0:
            return inc + 1
        elif inc < 0:
            return inc - 1
        else:
            return inc

    def __move_sequence_to_board(self, color):
        self.board = self.clear_board()
        coord_moves = Coder.decode_sequence(self.sequence)
        color_turn = 0

        for move in coord_moves:
            if color_turn % 2 == 0:
                self.board[move[0]][move[1]] = Coder.encode_game_string('black')
                self.__take_color_discs_on_move('black', move[0], move[1])
            else:
                self.board[move[0]][move[1]] = Coder.encode_game_string('white')
                self.__take_color_discs_on_move('white', move[0], move[1])
            color_turn += 1

    def __take_color_discs_on_move(self, color, i, j):
        for k in range(8):
            dir_y = [-1, -1, 0, 1, 1, 1, 0, -1]
            dir_x = [0, 1, 1, 1, 0, -1, -1, -1]

            history = []
            leave_searching = False

            while (i + dir_y[k] >= 0 and i + dir_y[k] < self.BOARD_SIZE) and (j + dir_x[k] >= 0 and j + dir_x[k] < self.BOARD_SIZE):
                new_i = i + dir_y[k]
                new_j = j + dir_x[k]

                if self.board[new_i][new_j] == Coder.encode_game_string(color):
                    if len(history) != 0:
                        for item in history:
                            self.board[item[0]][item[1]] = Coder.encode_game_string(color)
                    leave_searching = True
                elif self.board[new_i][new_j] == Coder.encode_game_string(None):
                    leave_searching = True
                else:
                    history.append((new_i, new_j))
                    dir_y[k] = self.__keep_same_direction_incrementer(dir_y[k])
                    dir_x[k] = self.__keep_same_direction_incrementer(dir_x[k])

                if leave_searching:
                    break



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

    def get_game_details(self, game_id):
        url = "https://www.eothello.com/get-game-updates"

        payload = f"game_id={game_id}&last_board_moves={self.sequence}&last_chat_message_id=-1"
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
        return (result['turn'], [] if self.sequence == '' else result['moves'], result['winner'])

    def make_move(self, game_id, move):
        url = "https://www.eothello.com/make-move"

        payload = f"game_id={game_id}&move={move}&move_index={self.move_index}"
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
        self.logger.log_info(f'Make move response code: {response.status_code}')
            
    def clear_board(self):
        board = [[Coder.encode_game_string(None) for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        board[3][3] = Coder.encode_game_string('white')
        board[3][4] = Coder.encode_game_string('black')
        board[4][3] = Coder.encode_game_string('black')
        board[4][4] = Coder.encode_game_string('white')
        return board
        





