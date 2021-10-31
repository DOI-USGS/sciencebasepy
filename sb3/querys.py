
def createMultipartUploadSession(s3FilePath):
    return f'''
        query {{
            createMultipartUploadSession(object: "{s3FilePath}")
        }}
    '''

def getPreSignedUrlForChunk(s3FilePath, upload_id, part_number):
    return f'''
        query {{
            getPreSignedUrlForChunk(object: "{s3FilePath}", upload_id: "{upload_id}", part_number: "{part_number}")
        }}
    '''

def completeMultiPartUpload(itemStr, upload_id, etag_payload):
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
