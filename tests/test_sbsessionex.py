import os
import getpass
import requests
import requests_mock
from sb3 import auth, client
import json
import pytest
import logging
import datetime
from sb3 import SbSessionEx

adapter = requests_mock.Adapter()

class TestClient:

    def test_cloud_upload(self, requests_mock):

        item_id = "5f9982f1d34e9cff790bd2fe"
        dname = os.path.dirname(__file__)
        fname = os.path.join(dname, "data/Python.jpg")
        GRAPHQL_URL = 'https://api-beta.staging.sciencebase.gov/graphql'

        presigned_url_repsonse = """
            {
                "data": {
                    "createMultipartUploadSession": "VERY_LONG_KEY",
                    "getPreSignedUrlForChunk": "https://presigned_very_long_url"
                }
            }
        """
        requests_mock.post(
            GRAPHQL_URL, json=json.loads(presigned_url_repsonse), status_code=200
        )

        requests_mock.put('https://presigned_very_long_url', 
                          headers = {"ETag":"etag_id"},
                          status_code=200)

        sbex = SbSessionEx.SbSessionEx(env='beta')

        #turn off authentication and refresh checks for this test
        sbex.refresh_token_before_expire = lambda *args, **kwargs: None
        sbex._authenticator.get_access_token = lambda *args, **kwargs: '1234'
        sbex._authenticator.get_token_expiry = lambda *args, **kwargs: datetime.datetime.today()

        sbex.upload_cloud_file_upload_session(item_id, fname)