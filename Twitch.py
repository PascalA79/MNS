import requests
from time import time
from app.models import Streamer
from utility import str_to_integer, try_retry
import os
class Twitch:
    BASE_URL = "https://api.twitch.tv/helix"
    __CLIENT_ID : str = ''
    __CLIENT_SECRET : str = ''
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Twitch, cls).__new__(cls)
        return cls._instance

    def __init__(self,client_id:str = None,client_secret:str = None):
        if client_id is None and client_secret is None:
            self.__CLIENT_ID = Twitch.__CLIENT_ID
            self.__CLIENT_SECRET = Twitch.__CLIENT_SECRET
        else:
            self.__CLIENT_ID = client_id
            self.__CLIENT_SECRET = client_secret
        self.__API_TOKEN,self.__EXPIRATION = self.__get_new_api_token()
        self.__EXPIRATION+=int(time())
        self.__headers={
            "Authorization": f"Bearer {self.__API_TOKEN}",
            "Client-ID": f"{self.__CLIENT_ID}",
        }

    @staticmethod
    def set_default_client(client_id : str,client_secret : str):
        Twitch.__CLIENT_ID = client_id
        Twitch.__CLIENT_SECRET = client_secret

    def __get_new_api_token(self):
        response = try_retry(requests.post, 5, 2, None, f" https://id.twitch.tv/oauth2/token?client_id={self.__CLIENT_ID}&client_secret={self.__CLIENT_SECRET}&grant_type=client_credentials")
        if response and response.status_code == 200:
            data = response.json()
            return data["access_token"], data["expires_in"]
        else:
            raise Exception(f"Error: get_new_api_token")

    def __check_token_valid(self):
        if(time()-60>self.__EXPIRATION):
            self.__API_TOKEN,self.__EXPIRATION=self.__get_new_api_token()
            self.__EXPIRATION+=int(time())

    def get_user_id(self, username: str) -> str:
        """
        Get the user ID of a streamer on Twitch.

        Parameters:
            - username: the username of the streamer

        Returns:
            The user ID of the streamer, or an empty string if the user could not be found.
        """
        self.__check_token_valid()
        # Make a request to the Twitch API to get information about the user
        params = {
            "login": username,
        }
        response = try_retry(requests.get, 5, 2, None, __class__.BASE_URL+"/users", headers=self.__headers, params = params)
        if not response:
            return '', ''
        data = response.json()

        # Get the user ID from the API response
        try:
            user_id = data["data"][0]["id"]
            name = data["data"][0]["display_name"]
        except (KeyError, IndexError):
            # User could not be found
            user_id = ''
            name = ''

        return (str_to_integer(user_id), name)
    
    def get_user_from_id(self, id_twitch: int):
            """
            Get the user on Twitch with the ID of the streamer.

            Parameters:
                - id_twitch: the ID of the streamer

            Returns:
                The user ID of the streamer, or an empty string if the user could not be found.
            """
            self.__check_token_valid()
            # Make a request to the Twitch API to get information about the user
            response = try_retry(requests.get, 5, 2, None, __class__.BASE_URL+f"/users?id={id_twitch}", headers=self.__headers)
            if not response:
                return '', ''
            data = response.json()

            # Get the user ID from the API response
            try:
                user_id = data["data"][0]["id"]
                name = data["data"][0]["display_name"]
            except (KeyError, IndexError):
                # User could not be found
                user_id = ''
                name = ''

            return (str_to_integer(user_id), name)

    def get_streaming_streamers(self, streamer_ids)->list:
        all_data = []  # Stocker toutes les données ici

        cursor = None
        while True:
            params = {"user_id": streamer_ids, "after": cursor}
            response = try_retry(requests.get, 5, 2, None, f"{self.BASE_URL}/streams", headers=self.__headers, params = params)
            if response and response.status_code == 200:
                data = response.json()
                stream_data = data.get("data", [])
                all_data.extend(stream_data)
                pagination = data.get("pagination", {})
                cursor = pagination.get("cursor")
                if not cursor:
                    break  # Il n'y a plus de pages à récupérer
            else:
                print(f"Errors: get_streaming_streamers")
                break
        
        return all_data

    def get_id_game(self,name):
        self.__check_token_valid()
        params = {"name": name}
        response = try_retry(requests.get, 5, 2, None, f"{self.BASE_URL}/games", headers=self.__headers, params=params)
        if not response:
            return '', ''
        data = response.json()
        try:
            id_game = data["data"][0]["id"]
            name_game = data["data"][0]["name"]
        except (KeyError, IndexError):
            # User could not be found
            id_game = ''
            name_game = ''
        return (str_to_integer(id_game), name_game)
    
    def get_profile_image(self, streamer_name:str)->str:
        headers = {
            "Client-ID": self.__CLIENT_ID,
            "Authorization": f"Bearer {self.__API_TOKEN}"
        }
        response = try_retry(requests.get, 5, 2, None, f"{self.BASE_URL}/users?login={streamer_name}", headers=headers)
        if not response:
            return ''
        data = response.json()
        try:
            return data["data"][0]["profile_image_url"]
        except (KeyError, IndexError):
            return ''

if __name__ == '__main__':
    from config import Config
    from time import sleep
    from datetime import datetime
    from dotenv import load_dotenv
    Config.default()
    load_dotenv()
    CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
    Twitch.set_default_client(CLIENT_ID, CLIENT_SECRET) 
    streamer_model = Streamer()
    list_streamer = [dict_id['id_twitch'] for dict_id in streamer_model.get(fields = ['id_twitch'])]
    twitch = Twitch()
    while True:
        list_streamer.append(712781192)
        info = twitch.get_streaming_streamers(list_streamer)
        game = twitch.get_id_game("super mario maker 2")

        for streamer in info:
            print(streamer)
            

            date_str = '2023-09-26T16:01:01Z'
            date_obj = datetime.fromisoformat(streamer['started_at'])

            # Vous pouvez également convertir le datetime en un objet timestamp en utilisant timestamp()
            date_timestamp = date_obj.timestamp()

            print(date_obj)         # Affiche la date et l'heure au format datetime
            print(int(date_timestamp)) 
        print("-------------------------------------------\n")
        sleep(3)
