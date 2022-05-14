import random
from soupsieve import match
from tensorflow import keras
from tensorflow.keras import layers, models, losses, Model
import tensorflow as tf
import numpy as np
from boardlogic import BoardLogic
from coder import Coder
import matplotlib.pyplot as plt
import math

from helpers import Helpers

class Predictor:

    def __init__(self, logger, 
                       color, 
                       location, 
                       checkpoint, 
                       max_loaded_matches,
                       split_validation,
                       model_type,
                       load_model, 
                       batch_size, 
                       epochs, 
                       debug = False):
        self.logger = logger
        self.debug = debug
        self.epochs = epochs
        self.batch_size = batch_size
        self.create_model(model_type)
        if load_model:
            self.model.load_weights(filepath=checkpoint)
        else:
            self.train_model(color, location, checkpoint, max_loaded_matches=max_loaded_matches, split_validation=split_validation)

    def create_model(self, model_type):
        if model_type == 'cnn':
            self.create_CNN_model()
        elif model_type == 'resnet':
            self.create_ResNet_model()

    # CNN model
    def create_CNN_model(self, scaled_board_size = 32, board_size = 8):
        self.model = models.Sequential()
        self.model.add(layers.Conv2D(filters=32, padding='same', kernel_size=(3,3), activation = "relu", input_shape=(scaled_board_size, scaled_board_size, 3)))
        self.model.add(layers.MaxPooling2D(pool_size=(2,2), padding='same'))
        self.model.add(layers.Conv2D(filters=64, padding='same', kernel_size=(3,3), activation = "relu"))
        self.model.add(layers.MaxPooling2D(pool_size=(2,2), padding='same'))
        self.model.add(layers.Conv2D(filters=64, padding='same', kernel_size=(3,3), activation = "relu"))
        self.model.add(layers.MaxPooling2D(pool_size=(2,2), padding='same'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(128, activation = "relu"))
        self.model.add(layers.Dropout(0.4))
        self.model.add(layers.Dense(64, activation = "relu"))
        self.model.add(layers.Dense(board_size * board_size))
        if self.debug:
            self.model.summary()
        self.model.compile(optimizer = "adam", loss = losses.SparseCategoricalCrossentropy(from_logits=True), metrics = ['acc'])
        self.probability_model = keras.Sequential([self.model, tf.keras.layers.Softmax()])

    def create_ResNet_model(self, scaled_board_size = 32, board_size = 8):
        base_model = tf.keras.applications.ResNet152(weights = 'imagenet', include_top = False, input_shape = (scaled_board_size, scaled_board_size, 3))
        # for layer in base_model.layers:
            # layer.trainable = False

        x = layers.Flatten()(base_model.output)
        x = layers.Dense(128, activation='relu')(x)
        predictions = layers.Dense(board_size * board_size, activation = 'softmax')(x)
        self.model = Model(inputs = base_model.input, outputs = predictions)
        if self.debug:
            self.model.summary()
        self.model.compile(optimizer='adam', loss=losses.sparse_categorical_crossentropy, metrics=['accuracy'])
        self.probability_model = keras.Sequential([self.model, tf.keras.layers.Softmax()])

    def train_model(self, color, location, checkpoint, max_loaded_matches, split_validation):
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

        register_after_move = 0

        max_loaded_matches = len(matches) if len(matches) < max_loaded_matches else max_loaded_matches
        self.logger.log_info(f'total matches: {max_loaded_matches}')

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
                        if color_turn >= register_after_move:
                            arr = Coder.get_numpy_array_from_board(board_logic.board)
                            train_data.append(arr)
                            i, j = Coder.decode_move(move)
                            move_index = Coder.get_move_as_numpy(i, j)
                            train_labels.append(move_index) 
                    
                    if (total_valid_moves_black > 0):
                        color_turn += 1
                else:
                    if (color == 'white' and total_valid_moves_white > 0) or (color == 'black' and total_valid_moves_black > 0 and total_valid_moves_white == 0):
                        if color_turn >= register_after_move:
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
                        if color_turn >= register_after_move:
                            arr = Coder.get_numpy_array_from_board(board_logic.board)
                            test_data.append(arr)
                            i, j = Coder.decode_move(move)
                            move_index = Coder.get_move_as_numpy(i, j)
                            test_labels.append(move_index) 
                    
                    if (total_valid_moves_black > 0):
                        color_turn += 1
                else:
                    if (color == 'white' and total_valid_moves_white > 0) or (color == 'black' and total_valid_moves_black > 0 and total_valid_moves_white == 0):
                        if color_turn >= register_after_move:
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

        self.model.fit(train_data, train_labels, batch_size=self.batch_size ,epochs=self.epochs, validation_data=(test_data, test_labels))  
        self.model.save_weights(filepath=checkpoint)


    def predict_move(self, board, valid_moves, scaled_board_size = 32):
        board_image = Coder.get_numpy_array_from_board(board)
        board_image = board_image.reshape((1, scaled_board_size, scaled_board_size, 3))
        board_heur = [100, -25, 10, 5, 5, 10, -25, 100,-25,-25,2,2,2,2,-25,-25,10,2,5,1,1,5,2,10,5,2,1,2,2,1,2,5,5,2,1,2,2,1,2,5,10,2,5,1,1,5,2,10,-25,-25,2,2,2,2,-25,-25,100,-25,10,5,5,10,-25,100]
        board_bench = [80, -26,24,-1,-5,28,-18,76,-23,-39,-18,-9,-6,-8,-39,-1,46,-16,4,1,-3,6,-20,52,-13,-5,2,-1,4,3,-12,-2,-5,-6,1,-2,-3,0,-9,-5,48,-13,12,5,0,5,-24,41,-27,-53,-11,-1,-11,-16,-58,-15,87,-25,27,-1,5,36,-3,100]

        pred = self.probability_model.predict(board_image)
        best_move = [(-1, -1), float('-inf')] # index, probability of move
        
        for i, j in valid_moves:
            move_index = Coder.get_move_as_numpy(i, j)[0]
            normalized_heur_move = Helpers.normalize(board_heur[move_index], -25, 100)
            normalized_bench_move = Helpers.normalize(board_bench[move_index], -58, 100)
            
            pred_value = pred[0][move_index]
            actual_value = math.log((pred_value * 0.5)) + math.log((normalized_heur_move * 0.20)) + math.log((normalized_bench_move * 0.30))
            if actual_value > best_move[1]:
                best_move[0] = (i, j)
                best_move[1] = actual_value

        return best_move[0]

    def predict_randomly(self, valid_moves):
        return random.choice(list(valid_moves))