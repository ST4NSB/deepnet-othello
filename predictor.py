import random

class Predictor:

    def __init__(self):
        pass

    def predict_randomly(self, valid_moves):
        return random.choice(list(valid_moves))