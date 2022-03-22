'''GraphQL Queries for interaction with ScienceBase Manager
'''
def create_multipart_upload_session(s3_filepath, content_type, username):
    '''create_multipart_upload_session
    '''
    return f'''
        query {{
            createMultipartUploadSession(
                object: "{s3_filepath}"
                contentType: "{content_type}"
                username: "{username}"               
            )
        }}
    '''

def get_presigned_url_for_chunk(s3_filepath, upload_id, part_number):
    '''get_presigned_url_for_chunk
    '''
    return f'''
        query {{
            getPreSignedUrlForChunk(object: "{s3_filepath}", upload_id: "{upload_id}", part_number: "{part_number}")
        }}
    '''

def complete_multipart_upload(item_str, upload_id, etag_payload):
    '''complete_multipart_upload
    '''
    etag_payload_array = str(etag_payload).replace("'","")

    return f'''
        query {{
            completeMultiPartUpload(
                    object: "{item_str}"
                    upload_id: "{upload_id}"
                    parts_eTags: {etag_payload_array}
            )
        }}
        
    '''
