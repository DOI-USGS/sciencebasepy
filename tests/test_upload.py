import requests
import requests_mock
from sb3 import auth, client
import json
import pytest
import logging

adapter = requests_mock.Adapter()


@pytest.mark.usefixtures('unstub')
class SbSessionEx:
    def getGraphQLURL(self):
        return "https://api-beta.staging.sciencebase.gov/graphql"

    def get_header(self):
        return {
            "content-type": "application/json",
            "accept": "application/json",
            "authorization": f"Bearer AUTHORIZATION_TOKEN",
        }

    def getLogger(self):
        return logging


class TestAuthenticator:
    def test_upload(self, requests_mock, monkeypatch):

        session = SbSessionEx()

        itemId = "5f9982f1d34e9cff790bd2fe"
        filename = "sample_error.png"
        file_path = "tests/resources/sample_error.png"
        GRAPHQL_URL = "https://api-beta.staging.sciencebase.gov/graphql"

        upload_url_repsonse = """
            {
                "data": {
                    "createUploadSession": { 
                        "uploads": [
                            {
                                "url": "https://LONG_URL_WITH_PRESIGNED_URL"
                            }
                        ]
                    }
                }
            }
        """

        upload_response = """
            {
                "data": {
                    "item": { "id": "5f9982f1d34e9cff790bd2fe", "title": "himal-test" },
                    "createUploadSession": {
                    "uploads": [
                        {
                        "name": "sample_error15.png",
                        "url": "https://dev-is-sb-beta-content.s3.us-west-2.amazonaws.com/5f9982f1d34e9cff790bd2fe/sample_error15.png?Content-Type=image%2Fjpeg&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIARGHURBUVAHB66GAH%2F20201104%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20201104T165505Z&X-Amz-Expires=900&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEID%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIAkbmAecgCiYj6SyH3mt4ELsf4BlTOXNaxIOk%2BjJtGmbAiAtXMRpH0iu3b%2BWZiCxDqkiAGV0Zw8alrFdIVOlb4eQRSq2AwjZ%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAIaDDA4MjExNzIwMTE5NCIMWH8ITDo7PNTAXJ2ZKooD8ae44Sse8ZXiska%2FQQadDUicK6y5JOFLT4f3xGhecvzPYSDcaH3cLz6vt7P6n49DyAzkkfbnw%2F2tFlvs5f8cOh1%2Bu1%2BBmDnHPFRxHhQufIykNQdDgKQzgTVKhuoQLYWXKG1Nha6PFP4hQRd88DZiFDMDP67qYByqdjvJOGHrtXO9ornSq5JjxxSjaJ0EUjCldmvxshnxCXFhaxu8c5Al5IoMspO2IligOeYl2tkzwDSXUW9oKHke0IgYdaN30i%2BbAiusMzn6dgiahIpozesptVsOmgdcRgOuFUR5lJCTuhv12uwbQfr9BmKR6pt4RQWHDQspgCiHzphS9olba4TkyYJ3B%2FuI%2BK6%2FLSWYBNyKvqJdcg61L8zh31dyBskhPgbBrbPMf9PlLEHkFBJesIMamf1%2B2IA1RYr3AUAt%2BcGk6hd%2BZ%2FX%2BO%2ByhlFExIrH9NtjGwqRlAD59Pooit82rYicXhd9rxKlqBYaCnl9Owj0bWNkRGycrYzDIlnP4taVY2mdDVCTp4%2BPoq4ryOTCJp4v9BTrsAYTK1WAqtLIP5Mf86SvlRqNb%2FLkJNI%2FNeZR7%2FHlVpb2sfnJMrcolWctU%2BKj906K4SNY6%2B752IDCiln%2BIkk77Z4PyFXibHx9%2Bdo9SV9fd6jDdMRy1OfZ98RVeP0dJ1q5gFGKpNMWBY8xR7lN%2BPBYStg5ffwy%2BiOH8I3yrMr1R9Nw66L5p0vfLGmQ%2FFz7AXmM7IKSQjAFnWy3OwEl36yc2QKVDsobTJLoFjSG%2Fgn925JSIYa4NjExERdLzx54jDpnvneQPBiip3ERvUmm4nk%2BaEQ7J0POwA7t6DR6L6hPIUscZcMOR42V7AEExI918&X-Amz-Signature=c1bf1c669cedbd5a4948b00dae65dd33a16db0be7cf6a67899976cb6a669f8b3&X-Amz-SignedHeaders=host%3Bx-amz-acl&x-amz-acl=private"
                        }
                    ]
                    }
                }
            }
        """

        requests_mock.post(
            GRAPHQL_URL, json=json.loads(upload_url_repsonse), status_code=200
        )
        requests_mock.put(
            "https://LONG_URL_WITH_PRESIGNED_URL",
            json=json.loads(upload_response),
            status_code=200,
        )

        client.upload_test_with_graphql_upload_session(
            itemId, filename, file_path, session=session
        )
