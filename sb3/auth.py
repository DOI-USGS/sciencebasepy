'''ScienceBase Keycloak Authentication Library
'''
import json
import requests
from datetime import datetime
import re

class DirectAccessAuthenticator:
    '''DirectAccessAuthenticator
    Authenticates with the Keycloak server using Direct Access
    '''
    _auth_token = None
    _base_url = None
    _realm = None
    _client_id = None
    _token_expiry = None

    def __init__(self, keycloak_uri, realm, client_id):
        """Handles authentication against a Keycloak auth server

        :param keycloak_uri: (str) The base URL for the keycloakserver
        :param realm: (str) The realm to authenticate with
        :param client_id: (str) Client id to use for authentication and refresh
        """
        self._keycloak_uri = keycloak_uri
        self._realm = realm
        self._client_id = client_id

    def authenticate(self, username, password):
        """authenticates against the Keycloak server with a provided username and password

        :param username: (str) The AD username
        :param password: (str) The AD password
        :raises TokenAuthenticationFailed: If authentication on server fails
        """
        payload = {
            "client_id": self._client_id,
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        token_resp = requests.post(self.get_token_server_uri(), data=payload)
        if token_resp.status_code == 200:
            token_resp_json = token_resp.json()
            self._auth_token = token_resp_json
            self._set_expiry()
        else:
            raise TokenAuthenticationFailed(token_resp, "Authentication")
        
    def authenticate_with_token(self, auth_token):
        """Use a provided token to authenticate with Keycloak
           Tries  to use the provided token to refresh to verify that the token works

        :param auth_token: (json) a json object that has "access_token" and "refresh_token" keys
        """
        self._auth_token = auth_token
        self.refresh_token()

    def revoke_token(self):
        """Revoke the current session tokens
        :raises TokenAuthenticationFailed: if the revoke operation fails
        """
        refresh_token = self.get_refresh_token()

        data = {
            "client_id": self._client_id,
            "refresh_token": refresh_token
        }
        token_resp = requests.post(self.get_revoke_server_uri(), data=data)
        if token_resp.status_code == 204:
            pass
        else:
            raise TokenAuthenticationFailed(token_resp, "Token Revoke")

        self.token = None
        self._token_expiry = None
        
        return True

    def refresh_token(self):
        """Refresh the token request on the server

        :raises TokenRefreshFailed: if the request returns a response except [200] 
        """
        data = {
            "client_id": self._client_id,
            "grant_type": "refresh_token",
            "refresh_token": self.get_refresh_token(),
        }
        token_resp = requests.post(self.get_token_server_uri(), data=data)

        if token_resp.status_code == 200:
            self._auth_token = token_resp.json()
            self._set_expiry()
        else:
            raise TokenAuthenticationFailed(token_resp, "Token Refresh")

    def _set_expiry(self):
        """Set the datetime when the current token will expire
        This is set to the soonest of the "token_expire" time and "token_refresh_expire" time
        contained in this instance's _auth_token
        """
        shortest_expire = min(self._auth_token['expires_in'], self._auth_token['refresh_expires_in'])
        token_expires_at = shortest_expire + (datetime.today()).timestamp()
        self._token_expiry = datetime.fromtimestamp(token_expires_at)

    def get_token_expiry(self):
        """Returns the datetime that the current token will expire
           uses the soonest of the token and refresh token times

        :return: (datetime) the soonest of the current token and refresh token times
        """
        return self._token_expiry 
        
    def get_access_token(self):
        '''get_access_token
        '''
        if self._auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() or provide_token() must run successfully "
                "before calling get_access_token"
            )
        return self._auth_token["access_token"]

    def get_refresh_token(self):
        '''get_refresh_token
        '''
        if self._auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self._auth_token["refresh_token"]

    def get_token_expire(self):
        '''get_token_expire
        '''
        if self._auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self._auth_token["expires_in"]

    def get_refresh_token_expire(self):
        '''get_refresh_token_expire
        '''
        if self._auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self._auth_token["refresh_expires_in"]

    def get_auth_server_uri(self):
        return f"{self._keycloak_uri}/realms/{self._realm}/protocol/openid-connect/auth"

    def get_token_server_uri(self):
        return f"{self._keycloak_uri}/realms/{self._realm}/protocol/openid-connect/token"

    def get_revoke_server_uri(self):
        return f"{self._keycloak_uri}/realms/{self._realm}/protocol/openid-connect/logout"

    def __str__(self):
        return json.dumps(self.auth_token)
    
    def get_username(self):
        """Fetches the username from the Keycloak userinfo endpoint.

        :return: (str) The username associated with the access token
        """
        if self._auth_token is None:
            raise ValueError("Authentication token is missing. Authenticate first.")

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}"
        }
        userinfo_url = f"{self._keycloak_uri}/realms/{self._realm}/protocol/openid-connect/userinfo"

        response = requests.get(userinfo_url, headers=headers)
        if response.status_code == 200:
            userinfo = response.json()
            return userinfo.get("preferred_username")
        else:
            raise TokenAuthenticationFailed(response, "Fetching User Info")

class TokenAuthenticationFailed(Exception):
    """Exception raised for errors returned when authenticating
    """
    def __init__(self, response, which='Authentication'):
        """Custom exception used to provide informative error messages from Keycloak 

        :param response: The response from the requests post
        :param which: (str) either 'Authentication' or 'Token Refresh', defaults to 'Authentication'
        """
        self.message = f"{which} Error: {str(response)}"
        try:
            self.message += re.sub('<[^<]+?>', '', response.text)
        except:
            self.message += response.reason

        super().__init__(self.message)
