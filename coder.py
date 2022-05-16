import numpy as np
import matplotlib.pyplot as plt

# class for encoding & decoding othello table
# 1 for black, -1 for white, 0 for none
class Coder:
    @staticmethod
    def encode_game_string(color):
        if color == 'black':
            return 'b'
        elif color == 'white': 
            return 'w'
        else: 
            return '.'

    @staticmethod
    def get_numpy_array_from_board(board, scale_up_board = 4, board_size = 8):
        arr = np.zeros(shape=(board_size, board_size, 3), dtype=float, order='F')

        for i in range(board_size):
            for j in range(board_size):
                if board[i][j] == Coder.encode_game_string('black'):
                    arr[i][j] = [0., 0., 1.]
                elif board[i][j] == Coder.encode_game_string('white'):
                    arr[i][j] = [1., 0., 0.]

        arr = arr.repeat(scale_up_board,axis=0).repeat(scale_up_board,axis=1) # this scales board up by $scale_up_board
        return arr

    @staticmethod
    def encode_move(i, j):
        move = str(chr(97 + j))
        move += str(i + 1)
        return move
    
    @staticmethod
    def decode_move(str):
        j = ord(str[0]) - 97
        i = int(str[1]) - 1
        return (i, j)

    @staticmethod
    def get_move_as_numpy(i, j, board_size = 8):
        k = np.array([0])
        for m in range(board_size):
            for n in range(board_size):
                if i == m and j == n:
                    return k
                k[0] += 1

        return k

    @staticmethod
    def get_move_as_coordinates(nr, board_size = 8):
        k = 0
        for i in range(board_size):
            for j in range(board_size):
                if k == nr:
                    return (i, j)
                k += 1  
                
        return (-1, -1)

    @staticmethod
    def decode_sequence(str):
        moves = []
        for i in range(0, len(str), 2):
            moves.append(Coder.decode_move(str[i:i+2]))
        return moves

    @staticmethod
    def get_sequence(str):
        moves = []
        for i in range(0, len(str), 2):
            moves.append((str[i:i+2]))
        return moves
