'''ScienceBase sbgraphql Client
'''
from pathlib import Path
from progress.bar import Bar
import requests
from sb3 import querys

_CHUNK_SIZE = 104857600  # 104857600 == 100MB
_REFRESH_TOKEN_SUBTRACTED = 600  # 10 * 60

def upload_cloud_file_upload_session(itemid, filename, file_path, session):
    '''upload_cloud_file_upload_session
    '''
    session.get_logger().info("upload_large_file_upload_session....")
    total_size = Path(file_path).stat().st_size
    total_chunks = int(total_size / _CHUNK_SIZE) + 1
    combine_str = itemid + "/" + filename

    query_create_multi_part = querys.create_multipart_upload_session(combine_str)

    session.get_logger().info(query_create_multi_part)

    # Refresh token add amount to expire
    session.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

    sb_resp = requests.post(
        session.get_graphql_url(),
        headers=session.get_header(),
        json={"query": query_create_multi_part},
    )

    session.get_logger().info(
        f"get_item query response, status code: {sb_resp.status_code}"
    )

    if sb_resp.status_code == 200:
        sb_resp_json = sb_resp.json()
        session.get_logger().info(sb_resp_json)
    else:
        sb_resp_json = sb_resp.json()
        session.get_logger().error(sb_resp_json)
        raise Exception("Not status 200")

    unique_id = sb_resp_json["data"]["createMultipartUploadSession"]

    session.get_logger().info("unique_id : " + unique_id)

    part_number = 0
    parts_header = []

    session.get_logger().info("session: " + str(session))
    session.get_logger().info("totalChunks: " + str(total_chunks))

    prog_bar = Bar("Uploading", max=total_chunks)
    with open(file_path, "rb") as f:
        for piece in _read_in_chunks(f):
            part_number = part_number + 1

            # Refresh token add amount to expire
            session.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

            session.get_logger().info(
                "time remaining : "
                + str(session.refresh_token_time_remaining(_REFRESH_TOKEN_SUBTRACTED))
            )

            queryCreatePresignedUrlPart = querys.get_presigned_url_for_chunk(
                combine_str, unique_id, part_number
            )
            session.get_logger().info(queryCreatePresignedUrlPart)

            sb_resp = requests.post(
                session.get_graphql_url(),
                headers=session.get_header(),
                json={"query": queryCreatePresignedUrlPart},
            )

            if sb_resp.status_code == 200:
                sb_resp_json = sb_resp.json()
                session.get_logger().info(sb_resp_json)
            else:
                sb_resp_json = sb_resp.json()
                session.get_logger().error(sb_resp_json)
                raise Exception("Not status 200")

            presignedUrl = sb_resp_json["data"]["getPreSignedUrlForChunk"]

            session.get_logger().info(presignedUrl)

            res = requests.put(presignedUrl, data=piece)

            if sb_resp.status_code != 200:
                raise Exception("Not status 200")

            eTag = res.headers["ETag"]
            parts_header.append({"ETag": eTag, "PartNumber": part_number})
            prog_bar.next()

            ##############################################################
            session.get_logger().info("+++++++++++++++++++++++++++++++++")
            session.get_logger().info(eTag)
            session.get_logger().info("+++++++++++++++++++++++++++++++++")
            ##############################################################
    prog_bar.finish()

    query_create_multi_part = querys.complete_multipart_upload(
        combine_str, unique_id, parts_header
    )

    session.get_logger().info(query_create_multi_part)

    session.refresh_token_before_expire(_REFRESH_TOKEN_SUBTRACTED)

    sb_resp = requests.post(
        session.get_graphql_url(),
        headers=session.get_header(),
        json={"query": query_create_multi_part},
    )

    if sb_resp.status_code == 200:
        sb_resp_json = sb_resp.json()
        session.get_logger().info(sb_resp_json)
    else:
        sb_resp_json = sb_resp.json()
        session.get_logger().error(sb_resp_json)
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
