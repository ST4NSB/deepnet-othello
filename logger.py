
class Logger:

    def log_info(self, msg):
        print(f'[INFO]: {msg}')

    def log_board(self, board, size):
        for i in range(size):
            for j in range(size):
                print(board[i][j], end =" ")
            print('')