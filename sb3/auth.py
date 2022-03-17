import requests
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)


class KeycloakClientConfig:
    """
    stores the Keycloak OIDC JSON with some properties pull out for convenience
    """

    def __init__(self, oidc_config):
        """
        pass in either a dict from the JSON config or a a path to the JSON config
        :param oidc_config: dict of the loaded JSON config
        """
        self.oidc_config = oidc_config

        self.client_id = oidc_config["resource"]
        # TODO: add support for a client.secret, oidc_config['credentials']['secret'], and update server calls to use it
        self._auth_server_uri = (
            f"{oidc_config['auth-server-url']}/realms/"
            f"{oidc_config['realm']}/protocol/openid-connect/auth"
        )
        self._token_server_uri = (
            f"{oidc_config['auth-server-url']}/realms/"
            f"{oidc_config['realm']}/protocol/openid-connect/token"
        )


class DirectAccessAuthenticator:
    def __init__(self, keycloak_config):
        if isinstance(keycloak_config, KeycloakClientConfig):
            self.keycloak_client_config = keycloak_config
        elif isinstance(keycloak_config, dict):
            self.keycloak_client_config = KeycloakClientConfig(keycloak_config)
        else:
            raise ValueError(
                "keycloak_config must be an instance of KeycloakClientConfig or dict (of the config data)"
            )

        self.auth_token = None

    def get_access_token(self):
        if self.auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_access_token"
            )
        return self.auth_token["access_token"]

    def get_refresh_token(self):
        if self.auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self.auth_token["refresh_token"]

    def get_token_expire(self):
        if self.auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self.auth_token["expires_in"]

    def get_refresh_token_expire(self):
        if self.auth_token is None:
            raise ValueError(
                "auth_token is missing, authenticate() must run successfully "
                "before calling get_refresh_token"
            )
        return self.auth_token["refresh_expires_in"]

    def authenticate(self, username=None, password=None, debug=False):

        payload = {
            "client_id": self.keycloak_client_config.client_id,
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        print(payload)

        print("self.keycloak_client_config._token_server_uri", self.keycloak_client_config._token_server_uri)
        token_resp = requests.post(
            self.keycloak_client_config._token_server_uri, data=payload
        )
        token_resp_json = token_resp.json()
        print(token_resp.status_code)
        print(token_resp_json)

        if debug:
            pp.pprint(token_resp_json)
        if token_resp.status_code != 200:
            print("failed")
            raise Exception("Authentication Failed")

        self.auth_token = token_resp_json
        #print(self.auth_token)

    def __str__(self):
        return json.dumps(self.auth_token)
