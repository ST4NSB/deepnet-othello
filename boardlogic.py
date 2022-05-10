
from coder import Coder

class BoardLogic:
    def __init__(self, color, board_size = 8):
        self.BOARD_SIZE = board_size
        self.board = self.clear_board()
        self.sequence = ''
        self.move_index = 2 if color == 'white' else 1

    def clear_board(self):
        board = [[Coder.encode_game_string(None) for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        board[3][3] = Coder.encode_game_string('white')
        board[3][4] = Coder.encode_game_string('black')
        board[4][3] = Coder.encode_game_string('black')
        board[4][4] = Coder.encode_game_string('white')
        return board

    def move_sequence_to_board(self):
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


    def get_valid_moves(self, color):
        valid_moves = set()
        
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] == Coder.encode_game_string(color):
                    valid_moves.update(self.__check_disc_every_direction(color, i, j))

        return valid_moves

    def get_scorepoints(self):
        black_points, white_points = 0, 0
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] == Coder.encode_game_string('black'):
                    black_points += 1
                elif self.board[i][j] == Coder.encode_game_string('white'):
                    white_points += 1

        return (black_points, white_points) 

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