import requests
import configparser
import base64
import json
import datetime
import os

class SpotifyAPI:
    """
    Spotify API connected through Ariel's Client
    https://stackoverflow.com/questions/48572494/structuring-api-calls-in-python
    """

    spotify_authorization_url = "https://accounts.spotify.com/authorize"
    token_url = "https://accounts.spotify.com/api/token"
    app_redirect = "http://localhost:8000/callback"


    def __init__(self):
        self.method_type = "ini"  # Setting the method_type attribute to "ini" within the __init__ method
        self.client_creds_refresh_time = datetime.datetime(1,1,1)
        self.client_creds_token = None
        self.auth_refresh_time = datetime.datetime(1,1,1)
        self.auth_token = None

    @property
    def _get_and_update_client_credentials_token(self):

        if self.method_type == "ini":
            parser = configparser.ConfigParser()
            auth_url = "https://accounts.spotify.com/api/token"
            try:
                parser.read("pipeline.ini")

                body_params = {
                    "grant_type": "client_credentials",
                    'json': True
                   }

                string_auth = str(
                    base64.b64encode(
                        (parser.get("SPOTIFY_CLIENT_CREDS", "CLIENT_ID") + ":" +
                         parser.get("SPOTIFY_CLIENT_CREDS", "CLIENT_SECRET"))
                        .encode("utf-8")
                    ),
                    "utf-8")
                headers = {
                    "Authorization": "Basic " + string_auth,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                response = requests.post(auth_url, headers=headers, data=body_params)
                if response.status_code != 200:
                    raise requests.exceptions.RequestException("Non-200 Response Code.")
                else:
                    self.refresh_time = datetime.timedelta(
                        seconds=json.loads(response.text)["expires_in"]) + datetime.datetime.now()
                    self.client_creds_token = json.loads(response.text)["access_token"]
                    return self.client_creds_token
            except FileNotFoundError as exc:
                print(exc.args)
            except requests.exceptions.RequestException as exc:
                print("Invalid Request: " + str(exc.args))
            except Exception as exc:
                print(exc.args)

    def _check_to_get_new_client_token(self):
        if datetime.datetime.now() > self.client_creds_refresh_time:
            return True

    def get_client_token(self):
        if self._check_to_get_new_client_token():
            return self._get_and_update_client_credentials_token
        else:
            return self.client_creds_token

    @property
    def _get_and_update_auth_token(self):
        # if self.method_type == "ini":
        try:
            parser = configparser.ConfigParser()

            os.chdir('/opt/airflow')
            parser_path = os.getcwd()
            parser_file = os.path.join(parser_path,
                                       ".config/pipeline.ini")
            print("parserFILE",parser_file)
            parser.read(parser_file)
            token_url = SpotifyAPI.token_url

            auth_options = {
                'url': token_url,
                'headers': {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Basic ' +
                    base64.b64encode(f'{parser.get("SPOTIFY_AUTH_CREDS", "CLIENT_ID")}:{parser.get("SPOTIFY_AUTH_CREDS", "CLIENT_SECRET")}'.encode()).decode()
                },
                'data': {
                    'grant_type': 'refresh_token',
                    'refresh_token': parser.get("SPOTIFY_AUTH_CREDS", "REFRESH_TOKEN")
                }
            }

            response = requests.post(**auth_options)

            if response.status_code != 200:
                raise requests.exceptions.RequestException("Non-200 Response Code.")
            else:
                self.auth_refresh_time = datetime.timedelta(
                    seconds=json.loads(response.text)["expires_in"]) + datetime.datetime.now()
                self.auth_token = json.loads(response.text)["access_token"]
                return self.auth_token

        except FileNotFoundError as exc:
            print(exc)
        except requests.exceptions.RequestException as exc:
            print("Invalid Request: " + str(exc.args))
        except Exception as exc:
            print(exc)

    def _check_to_get_new_auth_token(self):
        if datetime.datetime.now() > self.auth_refresh_time:
            return True

    def get_auth_token(self):
        if self._check_to_get_new_auth_token():
            return self._get_and_update_auth_token
        else:
            return self.auth_token


if __name__ == "__main__":
    spotify_auth = SpotifyAPI()


class SpotifyAPIData(SpotifyAPI):

    def __init__(self):
        super().__init__()
        self.token = super()._get_and_update_client_credentials_token()

    def create_get_request(self, url, headers=None):
        token = super().get_client_token()

        headers = {"Authorization": "Bearer " + token}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def make_post_request(self, url, data, headers=None):
        access_token = self.get_access_token()
        if headers is None:
            headers = {"Authorization": "Bearer " + access_token}
