'''ScienceBase sbgraphql Client
'''
from pathlib import Path
import os
import requests
from progress.bar import Bar

from sb3 import querys

_CHUNK_SIZE = 104857600  # 104857600 == 100MB
_REFRESH_TOKEN_SUBTRACTED = 600  # 10 * 60

def upload_cloud_file_upload_session(itemid, file_path, mimetype, sb_session_ex):
    '''upload_cloud_file_upload_session
    :param itemid ID of the ScienceBase Item to which to upload the file
    :param filename File name
    :param filepath Full path to the file
    :param sbsession_ex SbSessionEx which has been logged in via Keycloak
    '''
    sb_session_ex.get_logger().info("upload_large_file_upload_session....")
    total_size = Path(file_path).stat().st_size
    total_chunks = int(total_size / _CHUNK_SIZE) + 1
    fpath = f'{itemid}/{os.path.basename(file_path)}'

    query_create_multi_part = querys.create_multipart_upload_session(fpath, mimetype, sb_session_ex.get_current_user())

    sb_session_ex.get_logger().info(query_create_multi_part)

    # Refresh token add amount to expire
    sb_session_ex.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)
    requests_session = requests.session()

    sb_resp = requests_session.post(
        sb_session_ex.get_graphql_url(),
        headers=sb_session_ex.get_header(),
        json={"query": query_create_multi_part},
    )

    sb_session_ex.get_logger().info(
        f"get_item query response, status code: {sb_resp.status_code}"
    )

    if sb_resp.status_code == 200:
        sb_resp_json = sb_resp.json()
        sb_session_ex.get_logger().info(sb_resp_json)
    else:
        sb_resp_json = sb_resp.json()
        sb_session_ex.get_logger().error(sb_resp_json)
        raise Exception("Not status 200")

    unique_id = sb_resp_json["data"]["createMultipartUploadSession"]

    sb_session_ex.get_logger().info("unique_id : " + unique_id)

    part_number = 0
    parts_header = []

    sb_session_ex.get_logger().info("session: " + str(sb_session_ex))
    sb_session_ex.get_logger().info("totalChunks: " + str(total_chunks))

    prog_bar = Bar("Uploading", max=total_chunks)
    with open(file_path, "rb") as f:
        for piece in _read_in_chunks(f):
            part_number = part_number + 1

            # Refresh token add amount to expire
            sb_session_ex.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

            sb_session_ex.get_logger().info(
                "time remaining : "
                + str(sb_session_ex.refresh_token_time_remaining(_REFRESH_TOKEN_SUBTRACTED))
            )

            queryCreatePresignedUrlPart = querys.get_presigned_url_for_chunk(
                fpath, unique_id, part_number
            )
            sb_session_ex.get_logger().info(queryCreatePresignedUrlPart)

            sb_resp = requests_session.post(
                sb_session_ex.get_graphql_url(),
                headers=sb_session_ex.get_header(),
                json={"query": queryCreatePresignedUrlPart},
            )

            if sb_resp.status_code == 200:
                sb_resp_json = sb_resp.json()
                sb_session_ex.get_logger().info(sb_resp_json)
            else:
                sb_resp_json = sb_resp.json()
                sb_session_ex.get_logger().error(sb_resp_json)
                raise Exception("Not status 200")

            presignedUrl = sb_resp_json["data"]["getPreSignedUrlForChunk"]

            sb_session_ex.get_logger().info(presignedUrl)

            res = requests_session.put(presignedUrl, data=piece)

            if sb_resp.status_code != 200:
                raise Exception("Not status 200")

            eTag = res.headers["ETag"]
            parts_header.append({"ETag": eTag, "PartNumber": part_number})
            prog_bar.next()

            ##############################################################
            sb_session_ex.get_logger().info("+++++++++++++++++++++++++++++++++")
            sb_session_ex.get_logger().info(eTag)
            sb_session_ex.get_logger().info("+++++++++++++++++++++++++++++++++")
            ##############################################################
    prog_bar.finish()

    query_create_multi_part = querys.complete_multipart_upload(
        fpath, unique_id, parts_header
    )

    sb_session_ex.get_logger().info(query_create_multi_part)

    sb_session_ex.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

    sb_resp = requests_session.post(
        sb_session_ex.get_graphql_url(),
        headers=sb_session_ex.get_header(),
        json={"query": query_create_multi_part},
    )

    if sb_resp.status_code == 200:
        sb_resp_json = sb_resp.json()
        sb_session_ex.get_logger().info(sb_resp_json)
    else:
        sb_resp_json = sb_resp.json()
        sb_session_ex.get_logger().error(sb_resp_json)
        raise Exception("Not status 200")

    return sb_resp.json()


def _read_in_chunks(file_object, chunk_size=_CHUNK_SIZE):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1000k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
