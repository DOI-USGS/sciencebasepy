'''ScienceBase Keycloak Authentication Library
'''
import json
import requests

class KeycloakClientConfig:
    """Stores the Keycloak OIDC JSON with some properties pull out for convenience
    """
    _token_server_uri = None
    _auth_server_uri = None

    def __init__(self, oidc_config):
        """
        pass in either a dict from the JSON config or a a path to the JSON config
        :param oidc_config: dict of the loaded JSON config
        """
        self.oidc_config = oidc_config

        self.client_id = oidc_config["resource"]
        self._auth_server_uri = (
            f"{oidc_config['auth-server-url']}/realms/"
            f"{oidc_config['realm']}/protocol/openid-connect/auth"
        )
        self._token_server_uri = (
            f"{oidc_config['auth-server-url']}/realms/"
            f"{oidc_config['realm']}/protocol/openid-connect/token"
        )

    def get_token_server_uri(self):
        '''get_token_server_uri
        '''
        return self._token_server_uri

    def get_auth_server_uri(self):
        '''get_auth_server_uri
        '''
        return self._auth_server_uri

class DirectAccessAuthenticator:
    '''DirectAccessAuthenticator
    Authenticates with the Keycloak server using Direct Access
    '''
    def __init__(self, keycloak_config):
        if isinstance(keycloak_config, KeycloakClientConfig):
            self.keycloak_client_config = keycloak_config
        elif isinstance(keycloak_config, dict):
            self.keycloak_client_config = KeycloakClientConfig(keycloak_config)
        else:
            raise ValueError(
                "keycloak_config must be an instance of KeycloakClientConfig or dict of the config data"
            )

        self.auth_token = None

    def get_access_token(self):
        '''get_access_token
        '''
        if self.auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_access_token"
            )
        return self.auth_token["access_token"]

    def get_refresh_token(self):
        '''get_refresh_token
        '''
        if self.auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self.auth_token["refresh_token"]

    def get_token_expire(self):
        '''get_token_expire
        '''
        if self.auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self.auth_token["expires_in"]

    def get_refresh_token_expire(self):
        '''get_refresh_token_expire
        '''
        if self.auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self.auth_token["refresh_expires_in"]

    def authenticate(self, username=None, password=None):
        '''authenticate
        '''

        payload = {
            "client_id": self.keycloak_client_config.client_id,
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        token_resp = requests.post(
            self.keycloak_client_config.get_token_server_uri(), data=payload
        )
        token_resp_json = token_resp.json()

        if token_resp.status_code != 200:
            raise Exception("Authentication Failed")

        self.auth_token = token_resp_json

    def __str__(self):
        return json.dumps(self.auth_token)
