import requests
import requests_mock
from sb3 import auth
import json

adapter = requests_mock.Adapter()


class TestAuthenticator:
    def test_login(self, requests_mock):
        keycloak_client_config = {
            "realm": "ScienceBase-B",
            "auth-server-url": "https://www.sciencebase.gov/auth",
            "ssl-required": "external",
            "resource": "sb-steve-test-2",
            "public-client": True,
            "confidential-port": 0,
        }

        token_server_uri = (
            f"{keycloak_client_config['auth-server-url']}/realms/"
            f"{keycloak_client_config['realm']}/protocol/openid-connect/token"
        )

        return_json = """
        {
            "access_token": "REAL_LONG_ACCESS_TOKEN_STRING",
            "expires_in": 1800,
            "refresh_expires_in": 1800,
            "refresh_token": "REAL_LONG_REFRESH_TOKEN_STRING",
            "token_type": "bearer",
            "not-before-policy": 0,
            "session_state": "6f470ef1-d087-4fc1-9fe4-ab135dba02b4",
            "scope": "email profile"
        }
        """
        requests_mock.post(
            token_server_uri, json=json.loads(return_json), status_code=200
        )

        authenticator = auth.DirectAccessAuthenticator(keycloak_client_config)
        authenticator.authenticate("testuser", "testpassword")
        assert authenticator.get_access_token() == "REAL_LONG_ACCESS_TOKEN_STRING"