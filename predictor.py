import random
from soupsieve import match
from tensorflow import keras
from tensorflow.keras import layers, models, losses
import tensorflow as tf
import numpy as np
from boardlogic import BoardLogic
from coder import Coder
import matplotlib.pyplot as plt

from helpers import Helpers

class Predictor:

    def __init__(self, logger, checkpoint, epochs = 100, debug = False):
        self.logger = logger
        self.debug = debug
        self.epochs = epochs
        self.create_CNN_model()
        self.model.load_weights(filepath=checkpoint)

    # CNN model
    def create_CNN_model(self, board_size = 8):
        self.model = models.Sequential()
        self.model.add(layers.Conv2D(filters=64, kernel_size=(2,2), activation = "relu", input_shape=(board_size, board_size, 3)))
        self.model.add(layers.MaxPooling2D(pool_size=(2,2), strides=(2,2)))
        self.model.add(layers.Conv2D(filters=128, kernel_size=(2,2), activation = "relu"))
        self.model.add(layers.MaxPooling2D(pool_size=(2,2), strides=(4,4), padding='valid'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(128, activation = "relu"))
        self.model.add(layers.Dropout(0.4))
        self.model.add(layers.Dense(60, activation = "relu"))
        self.model.add(layers.Dense(board_size * board_size))
        if self.debug:
            self.model.summary()
        self.model.compile(optimizer = "adam", loss = losses.SparseCategoricalCrossentropy(from_logits=True), metrics = ['acc'])
        self.probability_model = keras.Sequential([self.model, tf.keras.layers.Softmax()])

    def train_model(self, color, location, checkpoint, max_loaded_matches = 5000, split_validation = 0.8):
        data = Helpers.get_games_from_dataset(location)
        matches = []
        for item in data:
            # item[1] is winner, item[2] is game moves
            if (color == 'black' and item[1] != '1') or (color == 'white' and item[1] != '-1'):
                continue
            matches.append(item[2])
        
        train_data = []
        train_labels = []
        test_data = []
        test_labels = []

        split_validation_count = int(split_validation * max_loaded_matches)
        for i in range(0, split_validation_count):
            match_moves = Coder.get_sequence(matches[i])
            board_logic = BoardLogic(color)

            color_turn = 0
            for move in match_moves:
                total_valid_moves_black = len(board_logic.get_valid_moves('black'))
                total_valid_moves_white = len(board_logic.get_valid_moves('white'))

                if color_turn % 2 == 0:
                    if (color == 'black' and total_valid_moves_black > 0) or (color == 'white' and total_valid_moves_white > 0 and total_valid_moves_black == 0):
                        arr = Coder.get_numpy_array_from_board(board_logic.board)
                        train_data.append(arr)
                        i, j = Coder.decode_move(move)
                        move_index = Coder.get_move_as_numpy(i, j)
                        train_labels.append(move_index) 
                    
                    if (total_valid_moves_black > 0):
                        color_turn += 1
                else:
                    if (color == 'white' and total_valid_moves_white > 0) or (color == 'black' and total_valid_moves_black > 0 and total_valid_moves_white == 0):
                        arr = Coder.get_numpy_array_from_board(board_logic.board)
                        train_data.append(arr)
                        i, j = Coder.decode_move(move)
                        move_index = Coder.get_move_as_numpy(i, j)
                        train_labels.append(move_index) 
                    
                    if (total_valid_moves_white > 0):
                        color_turn += 1    
                       
                board_logic.sequence += move
                board_logic.move_sequence_to_board()

        for i in range(split_validation_count, max_loaded_matches):
            match_moves = Coder.get_sequence(matches[i])
            board_logic = BoardLogic(color)

            color_turn = 0
            for move in match_moves:
                total_valid_moves_black = len(board_logic.get_valid_moves('black'))
                total_valid_moves_white = len(board_logic.get_valid_moves('white'))

                if color_turn % 2 == 0:
                    if (color == 'black' and total_valid_moves_black > 0) or (color == 'white' and total_valid_moves_white > 0 and total_valid_moves_black == 0):
                        arr = Coder.get_numpy_array_from_board(board_logic.board)
                        test_data.append(arr)
                        i, j = Coder.decode_move(move)
                        move_index = Coder.get_move_as_numpy(i, j)
                        test_labels.append(move_index) 
                    
                    if (total_valid_moves_black > 0):
                        color_turn += 1
                else:
                    if (color == 'white' and total_valid_moves_white > 0) or (color == 'black' and total_valid_moves_black > 0 and total_valid_moves_white == 0):
                        arr = Coder.get_numpy_array_from_board(board_logic.board)
                        test_data.append(arr)
                        i, j = Coder.decode_move(move)
                        move_index = Coder.get_move_as_numpy(i, j)
                        test_labels.append(move_index) 
                    
                    if (total_valid_moves_white > 0):
                        color_turn += 1    
                       
                board_logic.sequence += move
                board_logic.move_sequence_to_board()
                      
        train_data = np.asarray(train_data)
        train_labels = np.asarray(train_labels)
        test_data = np.asarray(test_data)
        test_labels = np.asfarray(test_labels)

        if self.debug: 
            self.logger.log_info(f'Loaded: {len(train_data)}, {len(train_labels)}, {len(test_data)}, {len(test_labels)},')

        self.model.fit(train_data, train_labels, epochs=self.epochs, validation_data=(test_data, test_labels))  
        self.model.save_weights(filepath=checkpoint)


    def predict_move(self, board, valid_moves, board_size = 8):
        board_image = Coder.get_numpy_array_from_board(board)
        board_image = board_image.reshape((1, board_size, board_size, 3))

        pred = self.probability_model.predict(board_image)
        while True:
            max_index = np.argmax(pred[0])
            if max_index == -1.0:
                break

            i, j = Coder.get_move_as_coordinates(max_index)
            if (i, j) in valid_moves:
                return (i, j)
            pred[0][max_index] = -1.0

        return self.predict_randomly(valid_moves)

    def predict_randomly(self, valid_moves):
        return random.choice(list(valid_moves))