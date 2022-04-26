from mimetypes import init
import requests
from helpers import *
import os
from dotenv import load_dotenv

# creates the game interface
class Game:

    def __init__(self, logger):
        self.logger = logger

    def create_game(self, color, bot_level = 1):

        load_dotenv()
        cookie = os.getenv('COOKIE')

        real_level = 2181 + bot_level
        url = f"https://www.eothello.com/add-challenge/{real_level}"

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
            'referer': f'https://www.eothello.com/create-challenge/{real_level}',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': f'{cookie}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        #print(response.text)
        game_function_details = Helpers.find_game_details(response.text)
        game_id = Helpers.get_first_number(game_function_details)

        self.logger.log_info(f'{game_id}, {type(game_id)}')




