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
    def decode_sequence(str):
        moves = []
        for i in range(0, len(str), 2):
            moves.append(Coder.decode_move(str[i:i+2]))
        return moves
        
