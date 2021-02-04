import requests
from requests_toolbelt.utils import dump
import json
import boto3
from botocore.exceptions import ClientError
import logging
from sb3 import querys
from pathlib import Path
import os
from datetime import datetime
from progress.bar import Bar

_CHUNK_SIZE = 104857600  # 104857600 == 100MB
_REFRESH_TOKEN_SUBTRACTED = 600  # 10 * 60


def get_item(session, itemId, params):
    query = querys.getItemQuery(itemId, params)

    session.getLogger().info(query)

    # Refresh token add amount to expire
    session.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

    sb_resp = requests.post(
        session.getGraphQLURL(), headers=session.get_header(), json={"query": query}
    )
    if sb_resp is None:
        print("sb_resp is null")
    else:
        print("sb session acquired")

    session.getLogger().info(
        f"get_item query response, status code: {sb_resp.status_code}"
    )
    if sb_resp.status_code == 200:
        sb_resp_json = sb_resp.json()
        session.getLogger().info(sb_resp_json)
    else:
        sb_resp_json = sb_resp.json()
        session.getLogger().error(sb_resp_json)

    return sb_resp.json()


def upload_test_with_graphql_upload_session(itemId, filename, file_path, session):
    session.getLogger().info(
        "---START upload_test_with_graphql_upload_session----------"
    )

    itemStr = f'id:"{itemId}"'
    itemIdStr = f'itemId:"{itemId}"'
    filenameStr = f'name:"{filename}"'
    fileContentType = f'contentType:"image/jpeg"'

    query = querys.createUploadSessionQuery(
        itemStr, itemIdStr, filenameStr, fileContentType
    )

    session.getLogger().info(query)

    # Refresh token add amount to expire
    session.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

    sb_resp = requests.post(
        session.getGraphQLURL(), headers=session.get_header(), json={"query": query}
    )

    sb_resp_dump = dump.dump_all(sb_resp)
    session.getLogger().info(f"--- graphql response, code {sb_resp.status_code} ---")
    session.getLogger().info(sb_resp_dump.decode("utf-8"))
    session.getLogger().info(sb_resp.text)
    session.getLogger().info(sb_resp.content)

    if sb_resp.status_code != 200:
        session.getLogger().error("Status Code is not 200")
        return

    sb_resp_json = sb_resp.json()
    session.getLogger().info(json.dumps(sb_resp_json, indent=4))

    upload_url = sb_resp_json["data"]["createUploadSession"]["uploads"][0]["url"]
    session.getLogger().info(f"upload_url:{upload_url}")

    with open(file_path, "rb") as f:
        files = {"file": (filename, f)}
        # http_response = requests.put(
        #     upload_url, files=files, headers={"content-type": "image/jpeg"}
        # )
        http_response = requests.put(upload_url, files=files)
    # If successful, returns HTTP status code 204
    if http_response.status_code >= 200 and http_response.status_code < 300:
        session.getLogger().info(
            f"File upload HTTP status code: {http_response.status_code}, encoding: {http_response.encoding} "
        )
        session.getLogger().info("---response text---")
        session.getLogger().info(http_response.text)
        session.getLogger().info("---response headers---")
        session.getLogger().info(http_response.headers)

    session.getLogger().info("---END upload_test_with_graphql_upload_session----------")
    return sb_resp_json


def upload_large_file_upload_session(itemId, filename, file_path, session):
    session.getLogger().info("upload_large_file_upload_session....")
    totalSize = Path(file_path).stat().st_size
    totalChunks = int(totalSize / _CHUNK_SIZE) + 1
    combineStr = itemId + "/" + filename
    print("**************************************************")
    print("Uploading file with size : ", totalSize)
    print("Number of chunks: ", totalChunks)
    print("**************************************************")

    queryCreateMultiPart = querys.createMultipartUploadSession(combineStr)

    session.getLogger().info(queryCreateMultiPart)

    # Refresh token add amount to expire
    session.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

    sb_resp = requests.post(
        session.getGraphQLURL(),
        headers=session.get_header(),
        json={"query": queryCreateMultiPart},
    )

    session.getLogger().info(
        f"get_item query response, status code: {sb_resp.status_code}"
    )

    if sb_resp.status_code == 200:
        sb_resp_json = sb_resp.json()
        session.getLogger().info(sb_resp_json)
    else:
        sb_resp_json = sb_resp.json()
        session.getLogger().error(sb_resp_json)
        raise Exception("Not status 200")

    unique_id = sb_resp_json["data"]["createMultipartUploadSession"]

    session.getLogger().info("unique_id : " + unique_id)

    part_number = 0
    parts_header = []

    session.getLogger().info("session: " + str(session))
    session.getLogger().info("totalChunks: " + str(totalChunks))

    bar = Bar("Uploading", max=totalChunks)
    with open(file_path, "rb") as f:
        for piece in _read_in_chunks(f):
            part_number = part_number + 1

            # Refresh token add amount to expire
            session.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

            session.getLogger().info(
                "time remaining : "
                + str(session.refresh_token_time_remaining(_REFRESH_TOKEN_SUBTRACTED))
            )

            queryCreatePresignedUrlPart = querys.getPreSignedUrlForChunk(
                combineStr, unique_id, part_number
            )
            session.getLogger().info(queryCreatePresignedUrlPart)

            sb_resp = requests.post(
                session.getGraphQLURL(),
                headers=session.get_header(),
                json={"query": queryCreatePresignedUrlPart},
            )
            if sb_resp.status_code == 200:
                sb_resp_json = sb_resp.json()
                session.getLogger().info(sb_resp_json)
            else:
                sb_resp_json = sb_resp.json()
                session.getLogger().error(sb_resp_json)
                raise Exception("Not status 200")

            presignedUrl = sb_resp_json["data"]["getPreSignedUrlForChunk"]

            session.getLogger().info(presignedUrl)

            res = requests.put(presignedUrl, data=piece)

            if sb_resp.status_code != 200:
                raise Exception("Not status 200")

            eTag = res.headers["ETag"]
            parts_header.append({"ETag": eTag, "PartNumber": part_number})
            bar.next()

            ##############################################################
            session.getLogger().info("+++++++++++++++++++++++++++++++++")
            session.getLogger().info(eTag)
            session.getLogger().info("+++++++++++++++++++++++++++++++++")
            ##############################################################
    bar.finish()

    queryCreateMultiPart = querys.completeMultiPartUpload(
        combineStr, unique_id, parts_header
    )

    session.getLogger().info(queryCreateMultiPart)

    session.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

    sb_resp = requests.post(
        session.getGraphQLURL(),
        headers=session.get_header(),
        json={"query": queryCreateMultiPart},
    )

    if sb_resp.status_code == 200:
        sb_resp_json = sb_resp.json()
        session.getLogger().info(sb_resp_json)
    else:
        sb_resp_json = sb_resp.json()
        session.getLogger().error(sb_resp_json)
        raise Exception("Not status 200")

    return sb_resp.json()


""" this will remain local """


def _read_in_chunks(file_object, chunk_size=_CHUNK_SIZE):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1000k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
