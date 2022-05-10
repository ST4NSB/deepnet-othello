import random
from soupsieve import match
from tensorflow import keras
from tensorflow.keras import layers, models, losses
import tensorflow as tf
import numpy as np

from helpers import Helpers

class Predictor:

    def __init__(self):
        pass

    # CNN model
    def create_model(self, board_size = 8):
        model = models.Sequential()
        model.add(layers.Conv2D(filters=12, kernel_size=(2,2), activation = "relu", input_shape=(board_size, board_size, 3)))
        model.add(layers.MaxPooling2D(pool_size=(2,2)))
        model.add(layers.Conv2D(filters=32, kernel_size=(2,2), activation = "relu"))
        model.add(layers.MaxPooling2D(pool_size=(2,2)))
        model.add(layers.Flatten())
        model.add(layers.Dropout(0.3))
        model.add(layers.Dense(256, activation = "relu"))
        model.add(layers.Dropout(0.5))
        model.add(layers.Dense(128, activation = "relu"))
        model.add(layers.Dropout(0.5))
        model.add(layers.Dense(board_size * board_size))
        model.summary()
        model.compile(optimizer = "adam", loss = losses.SparseCategoricalCrossentropy(from_logits=True), metrics = ['acc'])
        return model

    def train_model(self, color, location, split = 0.75):
        model = self.create_model()

        data = Helpers.get_games_from_dataset(location)
        matches = []
        for item in data:
            # item[1] is winner, item[2] is game moves
            if (color == 'black' and item[1] != '1') or (color == 'white' and item[1] != '-1'):
                continue
            matches.append(item[2])
        
        train_data = np.array([])
        train_labels = np.array([])
        test_data = np.array([])
        test_labels = np.array([])

        split_count = int(split * len(matches))
        for i in range(split_count):
            match = matches[i]

            





    def predict_randomly(self, valid_moves):
        return random.choice(list(valid_moves))