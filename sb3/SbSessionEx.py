import requests
import json
import logging
from sb3 import auth, client
from datetime import datetime


class SbSessionEx:
    """SbSessionEx encapsulates a session with ScienceBase, and provides extra methods for working with ScienceBase Catalog
    Items using GraphQL as well as authentication using keycloak.
    """

    def __init__(self, env=None):
        self._env = env
        self._logging = logging
        if env == "beta":
            self._graphql_url = "https://api-beta.staging.sciencebase.gov/graphql"
        elif env == "dev":
            self._graphql_url = "http://localhost:4000/graphql"
        else:
            self._graphql_url = "https://api.sciencebase.gov/graphql"

        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def getGraphQLURL(self):
        return self._graphql_url

    def loginEx(self, username, password):
        """Log into ScienceBase using Keycloak

        :param username: The ScienceBase user to log in as
        :param password: The ScienceBase password for the given user
        :return: The SbSessionEx object with the user logged in
        """
        print("calling loginEx")
        self._username = username

        try:
            print("try login")
            authenticator = _keycloak_login(username, password)

            print(authenticator)
            print(authenticator.get_token_expire())

            print("gotaccesstoken")
            #self._logging("info")
            #self._logging.info(authenticator)


            self._token = authenticator.get_access_token()
            self._refresh_token = authenticator.get_refresh_token()
            self._client_id = authenticator.keycloak_client_config.client_id
            self._token_server_uri = (
                authenticator.keycloak_client_config._token_server_uri
            )
            self._token_expire = authenticator.get_token_expire()
            print("token expire")
            print(self._token_expire)
            self._token_expire_refresh = authenticator.get_refresh_token_expire()
            self._token_expire_time = (
                self._token_expire + (datetime.today()).timestamp()
            )
            print("loginEx")
            print(self._token_expire_time)
        except Exception:
            self._logging.error("login failed for %s" % (username,))

        return self

    def getLogger(self):
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

    def upload_large_file_upload_session(self, itemId, filename, filepath):
        client.upload_large_file_upload_session(itemId, filename, filepath, self)

    def get_header(self):
        return {
            "content-type": "application/json",
            "accept": "application/json",
            "authorization": "Bearer " + self._token,
        }


def _keycloak_login(username, password):
    # TODO : check if resource is required
    keycloak_client_config = {
        "realm": "ScienceBase",
        "auth-server-url": "https://www.sciencebase.gov/auth",
        "ssl-required": "external",
        "resource": "sciencebasepy",
        "public-client": True,
        "confidential-port": 0,
    }

    authenticator = auth.DirectAccessAuthenticator(keycloak_client_config)

    authenticator.authenticate(username, password)

    #print(authenticator)
    return authenticator
