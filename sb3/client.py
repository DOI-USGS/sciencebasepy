'''ScienceBase sbgraphql Client
'''
from pathlib import Path
import os
import requests
from progress.bar import Bar
import mimetypes

from sb3 import querys

_CHUNK_SIZE = 104857600  # 104857600 == 100MB

def upload_cloud_file_upload_session(itemid, file_path, mimetype=None, sb_session_ex=None): 
    """_summary_

    :param itemid: (str) The identifier of the item to upload the file to
    :param file_path: Local file path to the file to upload
    :param mimetype: (str) The mime type of the file to upload.
                     If None is provided will guess the file type based on extension.
    :param sb_session_ex: (SBSessionEx) The session to use for the operation.

    :return: (json) The json item return from ScienceBase
    """

    sb_session_ex.get_logger().info("upload_large_file_upload_session....")
    total_size = Path(file_path).stat().st_size
    total_chunks = int(total_size / _CHUNK_SIZE) + 1
    fpath = f'{itemid}/{os.path.basename(file_path)}'

    if mimetype is None:
        mimetype = _guess_mimetype(file_path)

    query_create_multi_part = querys.create_multipart_upload_session(fpath, mimetype, sb_session_ex.get_current_user())

    sb_session_ex.get_logger().info(query_create_multi_part)

    # Refresh token add amount to expire
    sb_session_ex.refresh_token_before_expire()
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
            sb_session_ex.refresh_token_before_expire()

            sb_session_ex.get_logger().info(
                "time remaining : "
                + str(sb_session_ex.refresh_token_time_remaining())
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

    sb_session_ex.refresh_token_before_expire()

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

def bulk_cloud_download(selected_rows, sb_session_ex):
    query = """
          query getS3DownloadUrl($input: SaveFileInputs){
              getS3DownloadUrl(input: $input){
                downloadUri
              }
          }
        """

    variables = {"input": {"selectedRows": selected_rows}}

    requests_session = requests.session()

    sb_resp = requests_session.post(
                sb_session_ex.get_graphql_url(),
                headers=sb_session_ex.get_header(),
                json={'query': query, 'variables': variables}
            )

    if sb_resp.status_code != 200:
        sb_resp_json = sb_resp.json()
        sb_session_ex.get_logger().error(sb_resp_json)
        raise Exception("Not status 200")

    return sb_resp.json()

def publish_to_public_bucket(input, sb_session_ex):
    query = """
                mutation handleMFActions($input: ManageFileInput!) {
    handleMFActions(input: $input) {
      percent
      error
    }
  }
            """

    variables = {"input": input}

    requests_session = requests.session()

    sb_resp = requests_session.post(
        sb_session_ex.get_graphql_url(),
        headers=sb_session_ex.get_header(),
        json={'query': query, 'variables': variables}
    )

    if sb_resp.status_code != 200:
        sb_resp_json = sb_resp.json()
        sb_session_ex.get_logger().error(sb_resp_json)
        raise Exception("Not status 200")

    return sb_resp.json()

def unpublish_from_public_bucket(input, sb_session_ex):
    query = """
                mutation unpublishFile($input: UnpublishFileInput!){
                    unpublishFile(input: $input){
                      itemFile {
                        key
                      }
                    }
                }
            """

    variables = {"input": input}

    requests_session = requests.session()

    sb_resp = requests_session.post(
        sb_session_ex.get_graphql_url(),
        headers=sb_session_ex.get_header(),
        json={'query': query, 'variables': variables}
    )

    if sb_resp.status_code != 200:
        sb_resp_json = sb_resp.json()
        sb_session_ex.get_logger().error(sb_resp_json)
        raise Exception("Not status 200")

    return sb_resp.json()

def delete_cloud_file(input, sb_session_ex):
    query = """
                mutation deleteFile($input: DeleteFileInput!){
                    deleteFile(input: $input){
                        id
                    }
                }
            """

    variables = {"input": input}

    requests_session = requests.session()

    sb_resp = requests_session.post(
        sb_session_ex.get_graphql_url(),
        headers=sb_session_ex.get_header(),
        json={'query': query, 'variables': variables}
    )

    if sb_resp.status_code != 200 or 'errors' in sb_resp:
        print("Error:")
        print(sb_resp)
        print(sb_resp.text)
        print(sb_resp.status_code)
        sb_session_ex.get_logger().error(sb_resp)
        raise Exception("Not status 200")

    return sb_resp.text

def upload_s3_files(input, sb_session_ex): 
    query = """
                mutation uploadS3Files($input: UploadS3FilesInput!){
                    uploadS3Files(input: $input){
                      id 
                    }
                }
            """

    variables = {"input": input}

    requests_session = requests.session()

    sb_resp = requests_session.post(
        sb_session_ex.get_graphql_url(),
        headers=sb_session_ex.get_header(),
        json={'query': query, 'variables': variables}
    )

    if sb_resp.status_code != 200 or 'errors' in sb_resp.json():
        sb_session_ex.get_logger().error(sb_resp.json())
        raise Exception("Not status 200")

    return sb_resp.json()

def delete_item(input, sb_session_ex):
    query = """
            mutation DeleteItemQuery($input: DeleteItemInput!){
                deleteItem(input: $input){
                    itemId
                }
            }
        """

    variables = {"input": input}

    requests_session = requests.session()

    sb_resp = requests_session.post(
        sb_session_ex.get_graphql_url(),
        headers=sb_session_ex.get_header(),
        json={'query': query, 'variables': variables}
    )

    if sb_resp.status_code != 200 or 'errors' in sb_resp.json():
        sb_session_ex.get_logger().error(sb_resp.json())
        raise Exception("Not status 200")

    return sb_resp.json()

def _guess_mimetype(filename):
    """Guess mimetype of file

    :param filename: Name of file for which to guess mimetype
    :return: mimetype of file, or 'application/octet-stream' if it cannot be guessed
    """
    mimetype, _ = mimetypes.guess_type(filename)
    if mimetype is None:
        mimetype = 'application/octet-stream'
    return mimetype