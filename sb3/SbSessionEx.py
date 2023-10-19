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
    _auth_server_url = "https://www.sciencebase.gov/auth"
    _env = None
    _graphql_url = None
    _realm = None
    _username = None
    _client_id = None
    _authenticator = None

    def __init__(self, env=None, auth_refresh_time=300):
        self._env = env
        self._logging = logging
        self._auto_refresh_time=auth_refresh_time
        self._client_id = 'files-ui'
        if env == "beta":
            self._graphql_url = "https://api-beta.staging.sciencebase.gov/graphql"
            self._realm = "ScienceBase-B"
        elif env == "dev":
            self._graphql_url = "http://localhost:4000/graphql"
            self._realm = "ScienceBase-B"
        else:
            self._graphql_url = "https://api.sciencebase.gov/graphql"
            self._realm = "ScienceBase"

        self._authenticator = auth.DirectAccessAuthenticator(self._auth_server_url, self._realm, self._client_id)

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
            self._authenticator.authenticate(username, password)
        except Exception as e:
            self._logging.error(f"Keycloak login failed for {username} -- cloud services not available")
            raise

        return self

    def add_token(self, token_json):
        """Add in a token as a json or dictionary

        Args:
            token_json (_type_): _description_
        """
        self._authenticator.authenticate_with_token(token_json)

    def is_logged_in(self):
        '''Checks if the current refresh token can be refreshed. 
           If it has expired or can't be refreshed the user is not logged in
        '''
        try:
            self._authenticator.refresh_token()
            return True
        except:
            return False

    def get_current_user(self):
        '''get_current_user
        '''
        return self._username

    def get_logger(self):
        '''get_logger
        '''
        return self._logging

    def upload_cloud_file_upload_session(self, item_id, filename, mimetype=None):
        '''upload_large_file_upload_session
        '''
        return client.upload_cloud_file_upload_session(item_id, filename, mimetype, self)

    def bulk_cloud_download(self, selected_rows):
        '''generate bulk cloud download tokenized links
        '''
        return client.bulk_cloud_download(selected_rows, self)

    def upload_s3_files(self, input):
        '''upload external S3 bucket files to ScienceBase Item
        '''
        return client.upload_s3_files(input, self)

    def publish_to_public_bucket(self, input):
        '''publish file from public S3 bucket
        '''
        return client.publish_to_public_bucket(input, self)

    def unpublish_from_public_bucket(self, input):
        '''unpublish file from public S3 bucket
        '''
        return client.unpublish_from_public_bucket(input, self)

    def delete_cloud_file(self, input):
        '''delete files from ScienceBase item and S3 content bucket and/or S3 publish bucket
        '''
        return client.delete_cloud_file(input, self)

    def get_access_token(self):
        """_summary_

        :return: (str) 
        """
        return self._authenticator.get_access_token()

    def get_refresh_token(self):
        """Refresh tokens in ScienceBaseEx"""
        return self._authenticator.get_refresh_token()

    def refresh_token_before_expire(self, refresh_amount=None):
        """Refresh token if token has not expired, but will expire within some time,
        if token will expire with in that time then refresh will be triggered

        :refresh_amount: Amount subtracted (is seconds) from expired token value, that will trigger token refresh
        :return: True, if refresh is done, False, refresh is not triggered
        """
        if refresh_amount is None:
            refresh_amount = self._auto_refresh_time
        refresh_time = (datetime.today()).timestamp() + refresh_amount

        if self._authenticator.get_token_expiry().timestamp() - refresh_time < 0:
            self._authenticator.refresh_token()
            return True
        return False

    def refresh_token_time_remaining(self, refresh_amount=None):
        """Use for printing remaining time
        useful for debugging session timeout
        """
        if refresh_amount is None:
            refresh_amount = self._auto_refresh_time
        current_time = (datetime.today()).timestamp() + refresh_amount
        return self._authenticator.get_token_expiry() - current_time

    def revoke_token(self):
        """Revoke the tokens for the current session
        """
        self._authenticator.revoke_token()

    def get_header(self):
        '''get_header
        '''
        return {
            "content-type": "application/json",
            "accept": "application/json",
            "authorization": "Bearer " + self._authenticator.get_access_token(),
        }
