'''SbSessionEx provides a session object for working with ScienceBase GraphQL
'''
import json
import logging
from datetime import datetime
import requests
from sb3 import auth, client

class SbSessionEx:
    """SbSessionEx provides extra methods for working with ScienceBase GraphQL
    as well as authentication using Keycloak.
    """
    _env = None
    _graphql_url = None
    _realm = None
    _auth_server_url = None
    _username = None
    _token = None
    _refresh_token = None
    _client_id = None
    _token_server_uri = None
    _token_expire = None
    _token_expire_refresh = None
    _token_expire_time = None
    _is_logged_in = False

    def __init__(self, env=None):
        self._env = env
        self._logging = logging
        self._auth_server_url = "https://www.sciencebase.gov/auth"
        if env == "beta":
            self._graphql_url = "https://api-beta.staging.sciencebase.gov/graphql"
            self._realm = "ScienceBase-B"
        elif env == "dev":
            self._graphql_url = "http://localhost:4000/graphql"
            self._realm = "ScienceBase-B"
        else:
            self._graphql_url = "https://api.sciencebase.gov/graphql"
            self._realm = "ScienceBase"

    def get_graphql_url(self):
        '''get_graphql_url
        '''
        return self._graphql_url

    def login(self, username, password):
        """Log into ScienceBase using Keycloak

        :param username: The ScienceBase user to log in as
        :param password: The ScienceBase password for the given user
        :return: The SbSessionEx object with the user logged in
        """
        self._username = username

        try:
            authenticator = _keycloak_login(username, password, self._realm, self._auth_server_url)
            self._token = authenticator.get_access_token()
            self._refresh_token = authenticator.get_refresh_token()
            self._client_id = authenticator.keycloak_client_config.client_id
            self._token_server_uri = (
                authenticator.keycloak_client_config.get_token_server_uri()
            )
            self._token_expire = authenticator.get_token_expire()
            self._token_expire_refresh = authenticator.get_refresh_token_expire()
            self._token_expire_time = (
                self._token_expire + (datetime.today()).timestamp()
            )
            self._is_logged_in = True
        except Exception:
            self._logging.error(f"Keycloak login failed for {username} -- cloud services not available")
            self._is_logged_in = False

        return self

    def is_logged_in(self):
        '''is_logged_in
        '''
        return self._is_logged_in

    def get_current_user(self):
        '''get_current_user
        '''
        return self._username

    def get_logger(self):
        '''get_logger
        '''
        return self._logging

    def refresh_token(self):
        """Refresh tokens in ScienceBaseEx"""
        data = {
            "client_id": self._client_id,
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }
        token_resp = requests.post(self._token_server_uri, data=data)

        self._logging.info(token_resp.headers)
        self._logging.info(json.loads(token_resp.content.decode("utf-8")))

        if token_resp.status_code == 200:
            auth_token_json = token_resp.json()

            self._logging.info(auth_token_json)

            self._token = auth_token_json["access_token"]
            self._refresh_token = auth_token_json["refresh_token"]

            self._token_expire = auth_token_json["expires_in"]
            self._token_expire_refresh = auth_token_json["refresh_expires_in"]
            self._token_expire_time = (
                self._token_expire + (datetime.today()).timestamp()
            )
            self._logging.info("Token Refreshed.")
        else:
            raise Exception("Token Refreshed Failed.")

    def refresh_token_before_expire(self, refresh_amount):
        """Refresh token if token has not expired, but will expire with in some time,
        if token will expire with in that time then refresh will be triggered

        :refresh_amount: Amount subtracted (is seconds) from expired token value, that will trigger token refresh
        :return: True, if refresh is done, False, refresh is not triggered
        """
        current_time = (datetime.today()).timestamp() + refresh_amount

        if self._token_expire_time - current_time < 0:
            self.refresh_token()
            return True
        return False

    def refresh_token_time_remaining(self, refresh_amount):
        """Use for printing remaining time
        useful for debugging session timeout
        """
        current_time = (datetime.today()).timestamp() + refresh_amount
        return self._token_expire_time - current_time

    def upload_cloud_file_upload_session(self, item_id, filename, mimetype):
        '''upload_large_file_upload_session
        '''
        return client.upload_cloud_file_upload_session(item_id, filename, mimetype, self)

    def bulk_cloud_download(self, selected_rows):
        '''generate bulk cloud download tokenized links
        '''
        return client.bulk_cloud_download(selected_rows, self)

    def get_header(self):
        '''get_header
        '''
        return {
            "content-type": "application/json",
            "accept": "application/json",
            "authorization": "Bearer " + self._token,
        }

def _keycloak_login(username, password, realm, server_url):
    '''keycloak_login
    '''
    # Developer note: For some reason this method will not work inside the SbSessionEx class
    authenticator = auth.DirectAccessAuthenticator({
        "realm": realm,
        "auth-server-url": server_url,
        "ssl-required": "external",
        "resource": "sciencebasepy",
        "public-client": True,
        "confidential-port": 0,
    })
    authenticator.authenticate(username, password)

    return authenticator
