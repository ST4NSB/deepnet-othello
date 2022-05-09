from numpy import full
import requests
from helpers import *
from coder import *
import os
from dotenv import load_dotenv
import json

# creates the game interface on www.othello.com
class GameGym:
    def __init__(self, logger, predictor, agent, debug = False):
        load_dotenv()
        self.__cookie = os.getenv('COOKIE')
        self.BOARD_SIZE = 8
        self.logger = logger
        self.predictor = predictor
        self.agent = agent
        self.debug = debug

    def init_game(self, color, bot_level):
        # init
        self.board = self.clear_board()
        self.sequence = ''
        self.reward_history = []
        self.move_index = 2 if color == 'white' else 1

        # create game
        game_id = self.create_game_id(color, bot_level)

        # game logic
        turn, moves, winner = self.get_game_details(game_id)
        self.sequence = Helpers.convert_list_moves_to_string_moves(moves)
        self.__move_sequence_to_board()
        while turn != 'finished':
            self.calculate_move(game_id, color, turn)

            turn, moves, winner = self.get_game_details(game_id)
            new_sequence = Helpers.convert_list_moves_to_string_moves(moves)
            if len(new_sequence) >= len(self.sequence):
                self.sequence = new_sequence
            else:
                break
            self.move_index = len(self.sequence) // 2 + 1
            self.__move_sequence_to_board()

            self.reward_history.append(self.get_reward(color, turn))

        if self.debug:
            b, w = self.get_scorepoints()
            self.logger.log_info(f'move index: {self.move_index - 1}')
            self.logger.log_info(f'black score: {b}, white score: {w}')
            self.logger.log_info(f'reward: {self.get_reward(color, turn)}')
            self.logger.log_board(self.board, self.BOARD_SIZE)

        if not winner:
            b, w = self.get_scorepoints()
            r = b - w
            if r > 0:
                winner = 'black'
            elif r < 0:
                winner = 'white'
            else: 
                winner = 'equal'

        return (self.sequence, winner, self.reward_history)

    def get_reward(self, color, turn):
        opposite_color = 'white' if color == 'black' else 'black'
        black_points, white_points = self.get_scorepoints()
        
        score = (black_points - white_points) if color == 'black' else (white_points - black_points)
        score = self.__get_points_per_pieces(score)
        score = self.__get_points_per_corners(color, opposite_color, score)
        score = self.__get_points_per_danger_zones(color, opposite_color, score)
        score = self.__get_points_around_corner(color, opposite_color, score)
        score = self.__get_points_around_danger(color, opposite_color, score)
        score = self.__get_points_by_available_moves(color, opposite_color, turn, score)
        score = self.__get_points_by_middle_control(color, opposite_color, score)

        return score

    def __get_points_by_middle_control(self, color, opposite_color, points):
        middle_start = 2
        middle_end = 5
        positive_value = 1.1
        negative_value = 0.9

        for i in range(middle_start, middle_end):
            for j in range(middle_start, middle_end):
                if self.board[i][j] == Coder.encode_game_string(color):
                    points *= positive_value
                elif self.board[i][j] == Coder.encode_game_string(opposite_color):
                    points *= negative_value
        
        return points

    def __get_points_by_available_moves(self, color, opposite_color, turn, points):
        move_factor = 0.5
        if turn == color:
            points *= (len(self.get_valid_moves(color)) * move_factor)
        elif turn == opposite_color:
            points /= (len(self.get_valid_moves(opposite_color)) * move_factor)
        return points

    def __get_points_around_danger(self, color, opposite_color, points):
        positive_value = 1.3
        negative_value = 0.85
        
        for i in range(2, self.BOARD_SIZE - 3):
            if self.board[i][1] == Coder.encode_game_string(color):
                points *= negative_value
            elif self.board[i][1] == Coder.encode_game_string(opposite_color):
                points *= positive_value

        for i in range(2, self.BOARD_SIZE - 3):
            if self.board[i][self.BOARD_SIZE - 2] == Coder.encode_game_string(color):
                points *= negative_value
            elif self.board[i][self.BOARD_SIZE - 2] == Coder.encode_game_string(opposite_color):
                points *= positive_value

        for j in range(2, self.BOARD_SIZE - 3):
            if self.board[1][j] == Coder.encode_game_string(color):
                points *= negative_value
            elif self.board[1][j] == Coder.encode_game_string(opposite_color):
                points *= positive_value

        for j in range(2, self.BOARD_SIZE - 3):
            if self.board[self.BOARD_SIZE - 2][j] == Coder.encode_game_string(color):
                points *= negative_value
            elif self.board[self.BOARD_SIZE - 2][j] == Coder.encode_game_string(opposite_color):
                points *= positive_value
        
        return points

    def __get_points_around_corner(self, color, opposite_color, points):
        positive_value = 1.2
        negative_value = 0.9
        
        for i in range(1, self.BOARD_SIZE - 2):
            if self.board[i][0] == Coder.encode_game_string(color):
                points *= positive_value
            elif self.board[i][0] == Coder.encode_game_string(opposite_color):
                points *= negative_value

        for i in range(1, self.BOARD_SIZE - 2):
            if self.board[i][self.BOARD_SIZE - 1] == Coder.encode_game_string(color):
                points *= positive_value
            elif self.board[i][self.BOARD_SIZE - 1] == Coder.encode_game_string(opposite_color):
                points *= negative_value

        for j in range(1, self.BOARD_SIZE - 2):
            if self.board[0][j] == Coder.encode_game_string(color):
                points *= positive_value
            elif self.board[0][j] == Coder.encode_game_string(opposite_color):
                points *= negative_value

        for j in range(1, self.BOARD_SIZE - 2):
            if self.board[self.BOARD_SIZE - 1][j] == Coder.encode_game_string(color):
                points *= positive_value
            elif self.board[self.BOARD_SIZE - 1][j] == Coder.encode_game_string(opposite_color):
                points *= negative_value
        
        return points


    def __get_points_per_danger_zones(self, color, opposite_color, points):
        points *= self.__get_points_danger(color, opposite_color, 1, 1)
        points *= self.__get_points_danger(color, opposite_color, 1, self.BOARD_SIZE - 2)
        points *= self.__get_points_danger(color, opposite_color, self.BOARD_SIZE - 2, 1)
        points *= self.__get_points_danger(color, opposite_color, self.BOARD_SIZE - 2, self.BOARD_SIZE - 2)
        return points

    def __get_points_danger(self, color, opposite_color, i, j):
        if self.board[i][j] == Coder.encode_game_string(color):
            return 0.1
        elif self.board[i][j] == Coder.encode_game_string(opposite_color):
            return 1.85
        return 1.0

    def __get_points_per_corners(self, color, opposite_color, points):
        points *= self.__get_points_corner(color, opposite_color, 0, 0)
        points *= self.__get_points_corner(color, opposite_color, 0, self.BOARD_SIZE - 1)
        points *= self.__get_points_corner(color, opposite_color, self.BOARD_SIZE - 1, 0)
        points *= self.__get_points_corner(color, opposite_color, self.BOARD_SIZE - 1, self.BOARD_SIZE - 1)
        return points
    
    def __get_points_corner(self, color, opposite_color, i, j):
        if self.board[i][j] == Coder.encode_game_string(color):
            return 3.0
        elif self.board[i][j] == Coder.encode_game_string(opposite_color):
            return 0.03
        return 1.0

    def __get_points_per_pieces(self, score):
        lowest_difference = 1
        losing_advantage = 3
        
        table = self.BOARD_SIZE * self.BOARD_SIZE
        last_quarter_advantage = table - (table / 4)
        full_advantage = (table - 5)
        half_table = table / 2
        
        points = 1.0

        if score == table:
            points *= 100.0
        elif score == -table:
            points *= 0.00001
        elif score >= full_advantage:
            points *= 10.0
        elif score >= last_quarter_advantage:
            points *= 1.9
        elif score <= -full_advantage:
            points *= 0.01
        elif score <= -last_quarter_advantage:
            points *= 0.1
        elif score >= -lowest_difference and score <= lowest_difference:
            points *= 1.15
        elif score > losing_advantage and score < half_table:
            points *= (0.9 - (score * 0.1))
        else: 
            points *= 1.0

        return points

    def get_scorepoints(self):
        black_points, white_points = 0, 0
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] == Coder.encode_game_string('black'):
                    black_points += 1
                elif self.board[i][j] == Coder.encode_game_string('white'):
                    white_points += 1

        return (black_points, white_points)        

    def calculate_move(self, game_id, color, turn):
        valid_moves = self.get_valid_moves(color)
        if len(valid_moves) == 0:
            return

        if self.debug:
            encoded_moves = []
            for move in valid_moves:
                encoded_moves.append(Coder.encode_move(move[0], move[1]))
            self.logger.log_info(f'move index: {self.move_index}')
            self.logger.log_info(f'valid moves indexs: {valid_moves}')
            self.logger.log_info(f'valid moves: {encoded_moves}')
            b, w = self.get_scorepoints()
            self.logger.log_info(f'black score: {b}, white score: {w}')
            self.logger.log_info(f'reward: {self.get_reward(color, turn)}')
            self.logger.log_board(self.board, self.BOARD_SIZE)

        coord_move = list(valid_moves)[-1]
        if len(valid_moves) > 1:
            coord_move = self.predictor.predict_randomly(valid_moves)

        encoded_move = Coder.encode_move(coord_move[0], coord_move[1])

        self.make_move(game_id, encoded_move)
        self.sequence += encoded_move
        # self.move_index += 1
        # self.__move_sequence_to_board()

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

    def __move_sequence_to_board(self):
        self.board = self.clear_board()
        coord_moves = Coder.decode_sequence(self.sequence)
        color_turn = 0

        for move in coord_moves:
            if color_turn % 2 == 0:
                if move in self.get_valid_moves('black'):
                    self.board[move[0]][move[1]] = Coder.encode_game_string('black')
                    self.__take_color_discs_on_move('black', move[0], move[1])
                    color_turn += 1
                else:
                    self.board[move[0]][move[1]] = Coder.encode_game_string('white')
                    self.__take_color_discs_on_move('white', move[0], move[1])
            else:
                if move in self.get_valid_moves('white'):
                    self.board[move[0]][move[1]] = Coder.encode_game_string('white')
                    self.__take_color_discs_on_move('white', move[0], move[1])
                    color_turn += 1
                else:
                    self.board[move[0]][move[1]] = Coder.encode_game_string('black')
                    self.__take_color_discs_on_move('black', move[0], move[1])     

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

        if self.debug:
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
        return (result['turn'], [] if 'moves' not in result else result['moves'], result['winner'])

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
        if self.debug:
            self.logger.log_info(f'Make move response code: {response.status_code}')
            
    def clear_board(self):
        board = [[Coder.encode_game_string(None) for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        board[3][3] = Coder.encode_game_string('white')
        board[3][4] = Coder.encode_game_string('black')
        board[4][3] = Coder.encode_game_string('black')
        board[4][4] = Coder.encode_game_string('white')
        return board
        