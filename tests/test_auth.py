import requests
import requests_mock
from sb3 import auth
from sb3 import SbSessionEx
import sciencebasepy as pysb
import json
import time
import datetime


KEYCLOAK_URI = "https://www.sciencebase.gov/auth"
REALM = "ScienceBase-B"
CLIENT_ID = 'files-ui'

adapter = requests_mock.Adapter()

return_json_logon = """
{
    "access_token": "PW_TOKEN_STRING",
    "expires_in": 1800,
    "refresh_expires_in": 1800,
    "refresh_token": "REAL_LONG_REFRESH_TOKEN_STRING",
    "token_type": "bearer",
    "not-before-policy": 0,
    "session_state": "6f470ef1-d087-4fc1-9fe4-ab135dba02b4",
    "scope": "email profile"
}
"""

return_json_token_logon = """
{
    "access_token": "TOKEN_LOGON_STRING",
    "expires_in": 1800,
    "refresh_expires_in": 1800,
    "refresh_token": "REAL_LONG_REFRESH_TOKEN_LOGON_STRING",
    "token_type": "bearer",
    "not-before-policy": 0,
    "session_state": "6f470ef1-d087-4fc1-9fe4-ab135dba02b4",
    "scope": "email profile"
}
"""

return_json_token_refresh = """
{
    "access_token": "TOKEN_REFRESH_STRING",
    "expires_in": 1800,
    "refresh_expires_in": 1800,
    "refresh_token": "REAL_LONG_REFRESH_TOKEN_REFRESH_STRING",
    "token_type": "bearer",
    "not-before-policy": 0,
    "session_state": "6f470ef1-d087-4fc1-9fe4-ab135dba02b4",
    "scope": "email profile"
}
"""

class TestAuthenticator:

    def test_login(self, requests_mock):
        authenticator = auth.DirectAccessAuthenticator(KEYCLOAK_URI, REALM, CLIENT_ID)

        requests_mock.post(authenticator.get_token_server_uri(), 
            json=json.loads(return_json_logon), status_code=200)

        authenticator.authenticate("testuser", "testpassword")
        assert authenticator.get_access_token() == "PW_TOKEN_STRING"

    def test_token_authentication(self, requests_mock):
        authenticator = auth.DirectAccessAuthenticator(KEYCLOAK_URI, REALM, CLIENT_ID)

        requests_mock.post(authenticator.get_token_server_uri(), 
            json=json.loads(return_json_token_logon), status_code=200)
        
        token = {"access_token": "original_token",
                         "refresh_token": "original_refresh_token"}
        authenticator.authenticate_with_token(token)
        assert authenticator.get_access_token() == "TOKEN_LOGON_STRING"

    def test_token_refresh(self, requests_mock):
        authenticator = auth.DirectAccessAuthenticator(KEYCLOAK_URI, REALM, CLIENT_ID)

        requests_mock.post(authenticator.get_token_server_uri(), 
            json=json.loads(return_json_token_logon), status_code=200)
        
        token = {"access_token": "original_token",
                 "refresh_token": "original_refresh_token"}
        authenticator.authenticate_with_token(token)
        assert authenticator.get_access_token() == "TOKEN_LOGON_STRING"

        requests_mock.post(authenticator.get_token_server_uri(), 
            json=json.loads(return_json_token_refresh), status_code=200)
        authenticator.refresh_token()
        assert authenticator.get_access_token() == "TOKEN_REFRESH_STRING"


class TestSBSessionEx():
        
    def test_sbex_authentication(self, requests_mock):
        authenticator = auth.DirectAccessAuthenticator(KEYCLOAK_URI, REALM, CLIENT_ID)

        requests_mock.post(authenticator.get_token_server_uri(), 
            json=json.loads(return_json_logon), status_code=200)
                
        sb_session_ex = SbSessionEx.SbSessionEx(env="beta")

        sb_session_ex.login("testuser", "testpassword")
        assert sb_session_ex.is_logged_in()


class TestSBSession():
        
    def test_sb_authentication(self, requests_mock):
        authenticator = auth.DirectAccessAuthenticator(KEYCLOAK_URI, REALM, CLIENT_ID)

        requests_mock.post(authenticator.get_token_server_uri(), 
            json=json.loads(return_json_logon), status_code=200)
                
        sb_session = pysb.SbSession(env="beta")

        sb_session.login("testuser", "testpassword")
        assert sb_session.is_logged_in()

        requests_mock.post(authenticator.get_token_server_uri(), 
            json=json.loads(return_json_token_refresh), status_code=200)
        
        assert sb_session._sbSessionEx.get_access_token() == "PW_TOKEN_STRING"

        sb_session._sbSessionEx.refresh_token_before_expire()
        assert sb_session._sbSessionEx.get_access_token() == "PW_TOKEN_STRING"

        #Mock that the token is about to expire, so it get's refreshed here
        sb_session._sbSessionEx._authenticator._token_expiry = datetime.datetime.now() - datetime.timedelta(minutes=15)
        
        sb_session._sbSessionEx.refresh_token_before_expire()
        assert sb_session._sbSessionEx.get_access_token() == "TOKEN_REFRESH_STRING"
