import requests
import json
import os
import getpass
import logging
import mimetypes
from sb3 import auth, querys, client
from datetime import datetime
from sciencebasepy import SbSession


class SbSessionEx(SbSession):
    """SbSessionEx encapsulates a session with ScienceBase, and provides extra methods for working with ScienceBase Catalog
    Items using GraphQL as well as authentication using keycloak.
    """

    def __init__(self, env=None):
        super().__init__(env)
        self._env = env
        self._logging = logging
        if env == "beta":
            self._graphql_url = "https://api-beta.staging.sciencebase.gov/graphql"
            self._base_sb_url = "https://beta.sciencebase.gov/catalog/"
            # self._graphql_url = "https://dev-api.sciencebase.gov/graphql"
        elif env == "dev":
            self._base_sb_url = "https://beta.sciencebase.gov/catalog/"
            self._graphql_url = "http://localhost:4000/graphql"

            self._base_item_url = self._base_sb_url + "item/"
            self._base_items_url = self._base_sb_url + "items/"
            self._base_upload_file_url = self._base_sb_url + "file/uploadAndUpsertItem/"
            self._base_download_files_url = self._base_sb_url + "file/get/"
            self._base_upload_file_temp_url = self._base_sb_url + "file/upload/"
            self._base_item_link_url = self._base_sb_url + "itemLink/"
            self._base_move_item_url = self._base_items_url + "move/"
            self._base_undelete_item_url = self._base_item_url + "undelete/"
            self._base_shortcut_item_url = self._base_items_url + "addLink/"
            self._base_unlink_item_url = self._base_items_url + "unlink/"
            self._base_person_url = self._base_directory_url + "person/"
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
        self._username = username

        try:
            authenticator = _keycloak_login(username, password)

            self._logging.info(authenticator)

            self._token = authenticator.get_access_token()
            self._refresh_token = authenticator.get_refresh_token()
            self._client_id = authenticator.keycloak_client_config.client_id
            self._token_server_uri = (
                authenticator.keycloak_client_config._token_server_uri
            )
            self._token_expire = authenticator.get_token_expire()
            self._token_expire_refresh = authenticator.get_refresh_token_expire()
            self._token_expire_time = (
                self._token_expire + (datetime.today()).timestamp()
            )
        except Exception:
            self._logging.error("logging failed for %s" % (username,))

        # Also login using sciencebasepy
        super().login(username, password)

        return self

    def setLoggingEx(self, **kwargs):
        """Set Logging for ScienceBase, pass the same values as for logging in python

        :param **kwargs: parameters that you can pass to logging
        """
        self._logging = logging
        self._logging.basicConfig(**kwargs)

    def getLogger(self):
        return self._logging

    def get_token_expire_time(self):
        """Get Token expire time for a session in ScienceBaseEx

        :return: SbSessionEx time in seconds
        """
        return self._token_expire_time

    def logincEx(self, username):
        """Log into ScienceBase, prompting for the password, allows you to 5 tries

        :param username: The ScienceBase user to log in as
        :return: The SbSessionEx object with the user logged in
        """
        tries = 0
        while tries < 5:
            password = getpass.getpass()
            try:
                return self.loginEx(username, password)
            except Exception:
                tries += 1
                self._logging.error("Invalid password, try again")
        raise Exception(
            "Too many invalid password attemps, you may need to wait 15 minutes before trying again"
        )

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

    
    def refresh_token_on_expire(self):
        """Refresh token if token has expired then refresh will be triggered

        :return: True, if refresh is done, False, refresh is not triggered
        """
        current_time = (datetime.today()).timestamp()

        if self._token_expire_time - current_time < 0:
            self.refresh_token()
            return True
        return False

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

    def get_me(self):
        """Make a query to get information about current user

        :return: JSON information about current user
        """
        logging.info("-- me query --")
        query = f"{{ {querys.meQuery} }}"

        headers = self.get_header()

        self._logging.info(headers)

        sb_resp = requests.get(
            self._graphql_url, headers=headers, params={"query": query}
        )

        self._logging.info(f"me query response, status code: {sb_resp.status_code}")

        if sb_resp.status_code == 200:
            sb_resp_json = sb_resp.json()
            self._logging.info(sb_resp_json)
        else:
            sb_resp_json = sb_resp.json()
            self._logging.error(sb_resp_json)

        return sb_resp.json()

    def get_itemEx(self, itemId, params=["id", "title", "subTitle"]):
        """Return json with information concerning item in ScienceBase

        :param itemId: Item id
        :param params:
        :return: Return JSON information about item
        """
        return client.get_item(session=self, itemId=itemId, params=params)

    def upload_test_with_graphql_upload_session(self, itemId, filename, file_path):
        return client.upload_test_with_graphql_upload_session(
            itemId, filename, file_path, self
        )

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
        "realm": "ScienceBase-B",
        "auth-server-url": "https://www.sciencebase.gov/auth",
        "ssl-required": "external",
        "resource": "sb-steve-test-2",      
        "public-client": True,
        "confidential-port": 0,
    }

    authenticator = auth.DirectAccessAuthenticator(keycloak_client_config)

    print(authenticator)
    authenticator.authenticate(username, password)

    return authenticator
