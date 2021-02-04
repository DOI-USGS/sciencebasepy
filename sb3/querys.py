
import json

meQuery = """
    me {
        username
        myFolderExists
        myFolder {
          id
        }
        roles
    }
"""

#             createUploadSession({itemIdStr}, files : [{{ {filenameStr}, {fileContentType}}}]){{
def createUploadSessionQuery(itemStr, itemIdStr, filenameStr, fileContentType):
  return f'''
        {{
            item({itemStr}) {{
                id
                title
            }}
            createUploadSession({itemIdStr}, files : [{{ {filenameStr}}}]){{
                uploads {{
                    name
                    url
                }}
            }}
        }}'''


def getItemQuery(itemId, params):
    paramStr = make_param(params)
    return f'''
        query {{
            item(id: "{itemId}")
                {paramStr}
        }}
    '''

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


def make_param(mlist):
	mystr = '{ '
	for x in mlist:
		if type(x) == list:
			mystr = mystr  +  make_param(x)
		else:
			mystr = ' ' + mystr + ' ' + x + ' '
	mystr = mystr + ' }'
	return mystr
