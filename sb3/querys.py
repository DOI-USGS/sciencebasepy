'''GraphQL Queries for interaction with ScienceBase Manager
'''
def create_multipart_upload_session(s3FilePath):
    '''create_multipart_upload_session
    '''
    return f'''
        query {{
            createMultipartUploadSession(object: "{s3FilePath}")
        }}
    '''

def get_presigned_url_for_chunk(s3FilePath, upload_id, part_number):
    '''get_presigned_url_for_chunk
    '''
    return f'''
        query {{
            getPreSignedUrlForChunk(object: "{s3FilePath}", upload_id: "{upload_id}", part_number: "{part_number}")
        }}
    '''

def complete_multipart_upload(itemStr, upload_id, etag_payload):
    '''complete_multipart_upload
    '''
    etag_payload_array = str(etag_payload).replace("'","")

    return f'''
        query {{
            completeMultiPartUpload(
                    object: "{itemStr}"
                    upload_id: "{upload_id}"
                    parts_eTags: {etag_payload_array}
            )
        }}
        
    '''
