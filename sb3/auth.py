"""
Ex:
import fbauth
fbAuth = fbauth.TokenHandler(os.environ['FB_APP_ID'],
                os.environ['FB_APP_SECRET'])
access_token = fbAuth.get_access_token()
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib.request import urlopen
# from urllib.error import HTTPError
from webbrowser import open_new
import requests
import json
from urllib import parse
import os
from requests_toolbelt.utils import dump
from pathlib import Path
import getpass
import pprint

pp = pprint.PrettyPrinter(indent=4)

# TODO make port configurable to avoid conflicts
REDIRECT_URL = "http://localhost:8080"
PORT = 8080


def load_keycloak_config(keycloak_config_file_path):
    with open(keycloak_config_file_path) as keycloak_json_file:
        keycloak_client_config = json.load(keycloak_json_file)
        return keycloak_client_config


def collect_username_password():
    username = input("Enter Username: ")
    password = getpass.getpass(prompt="Enter Password: ", stream=None)
    return username, password


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


def get_token_from_code(code, keycloak_client_config: KeycloakClientConfig):
    print("get_token_from_code: " + code)

    # url = keycloak_client_config.token_server_uri + "?redirect_uri=" + REDIRECT_URL
    url = keycloak_client_config._token_server_uri
    data = {
        "client_id": keycloak_client_config.client_id,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URL,
    }
    print(f"url:{url}{os.linesep}data:{data}")

    token_resp = requests.post(
        url,
        data=data,
        headers={
            "Origin": "http://localhost:8080",
            "Referer": "http://localhost:8080/manager/",
        },
    )
    token_resp_dump = dump.dump_all(token_resp)
    print(token_resp_dump.decode("utf-8"))

    token_resp_json = token_resp.json()
    print("response:", json.dumps(token_resp_json, indent=4))

    return token_resp_json


class HTTPServerHandler(BaseHTTPRequestHandler):

    """
    HTTP Server callbacks to handle OAuth redirects
    """

    def __init__(
        self, request, address, server, keycloak_client_config: KeycloakClientConfig
    ):
        self.keycloak_client_config = keycloak_client_config
        self.client_id = keycloak_client_config.client_id
        # self.client_secret = keycloak_client_config.secret
        super().__init__(request, address, server)

    def do_GET(self):
        auth_uri = (
            f"{self.keycloak_client_config._token_server_uri}?client_id={self.client_id}&redirect_uri={REDIRECT_URL}"
        )

        print("auth_uri", auth_uri)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # print(f"path: {self.path}")
        # print(self.address_string())
        # print(self.requestline)
        if "code" in self.path:
            params = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            print("params: ", params)
            self.auth_code = params["code"]
            print(f"auth_code:{self.auth_code}")
            self.wfile.write(
                bytes(
                    "<html><h1>You may now close this window and return to your Python script."
                    + "</h1></html>",
                    "utf-8",
                )
            )
            self.server.access_token = get_token_from_code(
                self.auth_code, self.keycloak_client_config
            )

    # Disable logging from the HTTP Server
    def log_message(self, format, *args):
        return


class WebAuthorizationFlow:
    """
    drives the authorization flow which opens a browser for the login, gets a code from the response
    and then exchanges that for a token
    """

    def __init__(self, keycloak_client_config: KeycloakClientConfig = None):
        self.keycloak_client_config = keycloak_client_config

    def get_access_token(self):
        """
        start the authorization flow to get a code, by opening the browser
        """

        start_auth_uri = (
            self.keycloak_client_config.auth_server_uri
            + "?client_id="
            + self.keycloak_client_config.client_id
            + "&redirect_uri="
            + REDIRECT_URL
            + "&response_type=code&scope=openid"
        )

        print("start_auth_uri", start_auth_uri)

        open_new(start_auth_uri)
        http_server = HTTPServer(
            ("localhost", PORT),
            lambda request, address, server: HTTPServerHandler(
                request, address, server, self.keycloak_client_config
            ),
        )
        http_server.handle_request()
        return http_server.access_token


class Authenticator:
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
        raise NotImplemented

    def refresh(self, debug=False):
        data = {
            "client_id": self.keycloak_client_config.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self.get_refresh_token(),
        }
        token_resp = requests.post(
            self.keycloak_client_config._token_server_uri, data=data
        )
        if debug:
            token_resp_dump = dump.dump_all(token_resp)
            pp.pprint(token_resp_dump.decode("utf-8"))
        self.auth_token = token_resp.json()



#     logout?


class WebAuthFlowAuthenticator(Authenticator):
    def __init__(self, keycloak_client_config):
        super().__init__(keycloak_client_config)

    def authenticate(self):
        web_auth_flow = WebAuthorizationFlow(self.keycloak_client_config)
        self.auth_token = web_auth_flow.get_access_token()


class DirectAccessAuthenticator(Authenticator):
    def __init__(self, keycloak_client_config):
        super().__init__(keycloak_client_config)

    def authenticate(self, username=None, password=None, debug=False):

        payload = {
            "client_id": self.keycloak_client_config.client_id,
            "grant_type": "password",
            "username": username,
            "password": password,
        }

        print("self.keycloak_client_config._token_server_uri",self.keycloak_client_config._token_server_uri)
        token_resp = requests.post(
            self.keycloak_client_config._token_server_uri, data=payload
        )
        token_resp_json = token_resp.json()

        if debug:
            pp.pprint(token_resp_json)
        if token_resp.status_code != 200:
            raise Exception("Authentication Failed")

        self.auth_token = token_resp_json

    def __str__(self):
        return json.dumps(self.auth_token)
