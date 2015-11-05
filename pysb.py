#!/usr/bin/python
# requests is an optional library that can be found at http://docs.python-requests.org/en/latest/
import requests
import json
import os
import getpass
import logging
import httplib
import urlparse
import urllib
import mimetypes

class SbSession:
    _jossoURL = None
    _baseSbURL = None
    _baseItemURL = None
    _baseItemsURL = None
    _baseUploadFileURL = None
    _baseUploadFileTmpURL = None
    _baseDownloadFilesURL = None
    _baseMoveItemURL = None
    _baseUndeleteItemURL = None
    _usersId = None
    _username = None
    _jossosessionid = None
    _session = None
    
    #
    # Initialize session and set JSON headers
    #
    def __init__(self, env=None):
        if env == 'beta':
            self._baseSbURL = "https://beta.sciencebase.gov/catalog/"
            self._jossoURL = "https://my-beta.usgs.gov/josso/signon/usernamePasswordLogin.do"
            self._usersId = "4f4e4772e4b07f02db47e231"
        elif env == 'dev':
            self._baseSbURL = "http://localhost:8090/catalog/"
            self._jossoURL = "https://my-beta.usgs.gov/josso/signon/usernamePasswordLogin.do"
        else:
            self._baseSbURL = "https://www.sciencebase.gov/catalog/"
            self._jossoURL = "https://my.usgs.gov/josso/signon/usernamePasswordLogin.do"
            self._usersId = "4f4e4772e4b07f02db47e231"

        self._baseItemURL = self._baseSbURL + "item/"
        self._baseItemsURL = self._baseSbURL + "items/"
        self._baseUploadFileURL = self._baseSbURL + "file/uploadAndUpsertItem/"
        self._baseDownloadFilesURL = self._baseSbURL + "file/get/"
        self._baseUploadFileTmpURL = self._baseSbURL + "file/upload/"
        self._baseMoveItemURL = self._baseItemsURL + "move/"
        self._baseUndeleteItemURL = self._baseItemURL + "undelete/"

        self._session = requests.Session()
        self._session.headers.update({'Accept': 'application/json'})

    #
    # Log into ScienceBase
    #
    def login(self, username, password):
        # Save username
        self._username = username

        # Login and save JOSSO Session ID
        ret = self._session.post(self._jossoURL, params={'josso_cmd': 'josso', 'josso_username':username, 'josso_password':password})
        if ('JOSSO_SESSIONID' not in self._session.cookies):
            raise Exception("Login failed")
        self._jossosessionid = self._session.cookies['JOSSO_SESSIONID']
        self._session.params = {'josso':self._jossosessionid}

        return self

    #
    # Log out of ScienceBase
    #
    def logout(self):
        ret = self._session.post(self._baseSbURL + 'j_spring_security_logout')
        self._session.cookies.clear_session_cookies()
        self._session.params = {}

    #
    # Log into ScienceBase, prompting for the password
    #
    def loginc(self, username):
        password = getpass.getpass()
        return self.login(username, password)

    #
    # Return whether the SbSession is logged in and active in ScienceBase
    #
    def isLoggedIn(self):
        return self.getSessionInfo()['isLoggedIn']

    #
    # Ping ScienceBase.  A very low-cost operation to determine whether ScienceBase is available
    #
    def ping(self):
        return self.getJson(self._baseItemURL + 'ping')
        
    #
    # Return ScienceBase Josso session info
    #
    def getSessionInfo(self):
        return self.getJson(self._baseSbURL + 'jossoHelper/sessionInfo?includeJossoSessionId=true')

    #
    # Get the ScienceBase Item JSON with the given ID
    #
    # Returns JSON for the ScienceBase Item with the given ID
    #
    def getSbItem(self, itemid):
        ret = self._session.get(self._baseItemURL + itemid)
        return self._getJson(ret)
    
    #
    # Create a new Item in ScienceBase 
    #   
    def createSbItem(self, itemJson):
        ret = self._session.post(self._baseItemURL, data=json.dumps(itemJson))
        return self._getJson(ret)

    #
    # Update an existing ScienceBase Item
    #
    def updateSbItem(self, itemJson):
        ret = self._session.put(self._baseItemURL + itemJson['id'], data=json.dumps(itemJson))
        return self._getJson(ret)
        
    #
    # Delete an existing ScienceBase Item
    #
    def deleteSbItem(self, itemJson):
        ret = self._session.delete(self._baseItemURL + itemJson['id'], data=json.dumps(itemJson))
        self._checkErrors(ret)
        return True
    
    #
    # Undelete a ScienceBase Item
    #
    def undeleteSbItem(self, itemid):
        ret = self._session.post(self._baseUndeleteItemURL, params={'itemId': itemid})
        self._checkErrors(ret)
        return self._getJson(ret)
        
        
    #
    # Delete multiple ScienceBase Items.  This is much more
    # efficient than using deleteSbItem() for mass deletions, as it performs it server-side
    # in one call to ScienceBase.
    #
    def deleteSbItems(self, itemIds):
        idsJson = []
        for itemId in itemIds:
            idsJson.append({'id': itemId})        
        ret = self._session.delete(self._baseItemsURL, data=json.dumps(idsJson))
        self._checkErrors(ret)
        return True

    #
    # Move an existing ScienceBase Item under a new parent
    #
    def moveSbItem(self, itemid, parentid):
        ret = self._session.post(self._baseMoveItemURL, params={'itemId': itemid, 'destId': parentid})
        self._checkErrors(ret)
        return self._getJson(ret)

    #
    # Move ScienceBase Items under a new parent
    #
    def moveSbItems(self, itemids, parentid):
        count = 0
        if itemids:
            for itemid in itemids:
                print 'moving ' + itemid
                self.moveSbItem(itemid, parentid)
                count += 1
        return count

    #
    # Upload a file to an existing Item in ScienceBase
    #
    def uploadFileToItem(self, item, filename):        
        return self.uploadFilesAndUpdateItem(item, [filename])
        
    #
    # Upload a file and create a new Item in ScienceBase
    #
    def uploadFileAndCreateItem(self, parentid, filename):        
        return self.uploadFilesAndCreateItem(parentid, [filename])    

    #
    # Upload multiple files and create a new Item in ScienceBase
    #
    def uploadFilesAndCreateItem(self, parentid, filenames):
        url = self._baseUploadFileURL
        files = []
        for filename in filenames:
            if (os.access(filename, os.F_OK)):
                files.append(('file', open(filename, 'rb')))
            else:
                raise Exception("File not found: " + filename)
        ret = self._session.post(url, files=files, params={'parentId': parentid})
        return self._getJson(ret)
        
    #
    # Upload multiple files and update an existing Item in ScienceBase
    #
    def uploadFilesAndUpdateItem(self, item, filenames):
        url = self._baseUploadFileURL
        files = []
        for filename in filenames:
            if (os.access(filename, os.F_OK)):
                files.append(('file', open(filename, 'rb')))
            else:
                raise Exception("File not found: " + filename)
        ret = self._session.post(url, files=files, data={'id': item['id'], 'item': json.dumps(item)})
        return self._getJson(ret)
        
    #
    # Upload a file to ScienceBase.  The file will be staged in a temporary area.  In order
    # to attach it to an Item, the pathOnDisk must be added to an Item files entry, or
    # one of a facet's file entries.
    #
    def uploadFile(self, filename, mimetype=None):
        retval = None    
        url = self._baseUploadFileTmpURL
    
        if (os.access(filename, os.F_OK)):
            files = {'file': open(filename, 'rb')}
            #
            # if no mimetype was sent in, try to guess
            #
            if None == mimetype:
                mimetype = mimetypes.guess_type(filename)
            (dir, fname) = os.path.split(filename)
            ret = self._session.post(url, files=[('files[]', (fname, open(filename, 'rb'), mimetype))])
            retval = self._getJson(ret)
        else:
            raise Exception("File not found: " + filename)
        return retval

    #
    # Replace a file on a ScienceBase Item.  This method will replace all files named
    # the same as the new file, whether they are in the files list or on a facet.
    #
    def replaceFile(self, filename, item):
        (dir, fname) = os.path.split(filename)        
        #  
        # replace file in files list
        #
        if 'files' in item:  
            newFiles = []
            for file in item['files']:
                if file['name'] == fname:   
                    file = self._replaceFile(filename, file)      
                newFiles.append(file)
            item['files'] = newFiles
        #
        # replace file in facets
        #
        if 'facets' in item:
            newFacets=[]
            for facet in item['facets']:
                if 'files' in facet:
                    newFiles = []
                    for file in facet['files']:
                        if file['name'] == fname:
                            file = self._replaceFile(filename, file)                           
                        newFiles.append(file)
                    facet['files'] = newFiles
                    newFacets.append(facet)
            item['facets'] = newFacets                      
        self.updateSbItem(item)    
        
    #
    # Upload a file to ScienceBase and update file json with new path on disk.
    #
    def _replaceFile(self, filename, file):        
        #
        # Upload file and point file JSON at it
        #
        upldJson = self.uploadFile(filename, file['contentType'])
        file['pathOnDisk'] = upldJson[0]['fileKey']
        file['dateUploaded'] = upldJson[0]['dateUploaded']
        file['uploadedBy'] = upldJson[0]['uploadedBy'] 
        return file                         
        
    #
    # Download all files from a ScienceBase Item as a zip.  The zip is created server-side
    # and streamed to the client.
    #
    def getItemFilesZip(self, item, destination = '.'):
        #
        # First check that there are files attached to the item, otherwise the call
        # to ScienceBase will return an empty zip file
        #
        fileInfo = self.getItemFileInfo(item)
        if not fileInfo:
            return None
            
        #
        # Download the zip
        #
        r = self._session.get(self._baseDownloadFilesURL + item['id'], stream=True) 
        local_filename = os.path.join(destination, item['id'] + ".zip")
        
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename     
        
    #
    # Retrieve file information from a ScienceBase Item.  Returns a list of dictionaries
    # containing url, name and size of each file.
    #
    def getItemFileInfo(self, item):
        retval = []
        if item: 
            #
            # regular files
            #
            if 'files' in item: 
                for file in item['files']:
                    retval.append({'url': file['url'], 'name': file['name'], 'size': file['size']})
            if 'facets' in item:
                for facet in item['facets']:
                    for file in facet['files']:
                        retval.append({'url': file['url'], 'name': file['name'], 'size': file['size']})
        return retval
        
    #
    # Download file from URL
    #
    def downloadFile(self, url, local_filename, destination = '.'):
        completeName = os.path.join(destination, local_filename) 
        print "downloading " + url + " to " + completeName
        r = self._session.get(url, stream=True)        
        
        with open(completeName, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return completeName          
        
    #
    # Download the individual files attached to a ScienceBase Item
    #
    def getItemFiles(self, item, destination = '.'):
        fileInfo = self.getItemFileInfo(item)
        for fileInfo in fileInfo:
            self.downloadFile(fileInfo['url'], fileInfo['name'], destination)
        return fileInfo
            
    #
    # Get the ID of the logged-in user's My Items
    #
    def getMyItemsId(self):    
        if (self._username):
            params = {'q': '', 'lq': 'title.untouched:"' + self._username + '"'}
            if self._usersId:
                params['parentId'] = self._usersId
            items = self.findSbItems(params)
            if ('items' in items): 
                for item in items['items']:
                    if (item['title'] == self._username):
                        return item['id']

    #
    # Get IDs of all children for a given parent
    #
    def getChildIds(self, parentid):
        retval = []
        items = self.findSbItems({'parentId': parentid})
        while items and 'items' in items:
            for item in items['items']:
                retval.append(item['id'])
            items = self.next(items)
        return retval
                        
    #
    # WORK IN PROGRESS
    # Given an OPEeNDAP URL, create a NetCDFOPeNDAP facet from the return data
    #
    def getNetCDFOPeNDAPInfoFacet(self, url):
        data = self._getJson(self._session.post(self._baseSbURL + 'items/scrapeNetCDFOPeNDAP', params={'url': url}))
        facet = {}
        facet['className'] = 'gov.sciencebase.catalog.item.facet.NetCDFOPeNDAPFacet'
        facet['title'] = data['title']
        facet['summary'] = data['summary']
        facet['boundingBox'] = {}    
        facet['boundingBox']['minX'] = data['boundingBox']['minX']
        facet['boundingBox']['maxX'] = data['boundingBox']['maxX']
        facet['boundingBox']['minY'] = data['boundingBox']['minY']
        facet['boundingBox']['maxY'] = data['boundingBox']['maxY']
        facet['variables'] = data['variables'] 
        return facet
    
    #
    # Search for ScienceBase items
    #
    def findSbItems(self, params):
        return self._getJson(self._session.get(self._baseItemsURL, params=params))

    #
    # Get the next set of items from the search
    #
    def next(self, items):
        retVal = None
        if 'nextlink' in items:
            retVal = self._getJson(self._session.get(self._removeJossoParam(items['nextlink']['url'])))
        return retVal

    #
    # Get the previous set of items from the search
    #
    def previous(self, items):
        retVal = None
        if 'prevlink' in items:
            retVal = self._getJson(self._session.get(self._removeJossoParam(items['prevlink']['url'])))
        return retVal

    #
    # Search for ScienceBase items by free text
    #
    def findSbItemsByAnytext(self, text):
        return self.findSbItems({'q': text})

    #
    # Search for ScienceBase items by title
    #
    def findSbItemsByTitle(self, text):
        return self.findSbItems({'q': '', 'lq': 'title:"' + text + '"'})

    #
    # Get the text response of the given URL
    #
    def get(self, url):
        return self._getText(self._session.get(url))

    #
    # Get the JSON response of the given URL
    #
    def getJson(self, url):
        return self._getJson(self._session.get(url))        

    #
    # Check the status code of the response, and return the JSON
    #    
    def _getJson(self, response):     
        self._checkErrors(response)
        try:
            return response.json()
        except:
            raise Exception("Error parsing JSON response")

    #
    # Check the status code of the response, and return the text
    #
    def _getText(self, response):
        self._checkErrors(response)
        try:
            return response.text
        except:
            raise Exception("Error parsing response")

    #
    # Check the status code of the response
    #
    def _checkErrors(self, response):
        if (response.status_code == 404):
            raise Exception("Resource not found, or user does not have access")
        elif (response.status_code == 401):
            raise Exception("Unauthorized access")
        elif (response.status_code != 200):
            raise Exception("Other HTTP error: " + str(response.status_code) + ": " + response.text)
            
    #
    # Remove josso parameter from URL
    #
    def _removeJossoParam(self, url):
        o = urlparse.urlsplit(url)
        q = [x for x in urlparse.parse_qsl(o.query) if "josso" not in x]
        return urlparse.urlunsplit((o.scheme, o.netloc, o.path, urllib.urlencode(q), o.fragment))
        
    #
    # Turn on HTTP logging for debugging purposes
    #            
    def debug(self):                
        # This line enables debugging at httplib level (requests->urllib3->httplib)
        # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
        # The only thing missing will be the response.body which is not logged.
        httplib.HTTPConnection.debuglevel = 1

        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig() 
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

#
# Main    
#
if __name__ == "__main__":
    sb = SbSession()

    # Get a public item.  No need to log in.
    itemJson = sb.getSbItem('505bc673e4b08c986b32bf81')
    print "Public Item: " + str(itemJson)

    # Get a private item.  Need to log in first.
    username = raw_input("Username:  ")
    sb.loginc(str(username))

    itemJson = sb.getSbItem(sb.getMyItemsId())
    print "My Items: " + str(itemJson)

    # Create a new item.  The minimum required is a title for the new item, and the parent ID
    newItem = {'title': 'This is a new test item',
        'parentId': sb.getMyItemsId(),
        'provenance': {'annotation': 'Python ScienceBase REST test script'}}
    newItem = sb.createSbItem(newItem)
    print "NEW ITEM: " + str(newItem)

    # Upload a file to the newly created item
    newItem = sb.uploadFileToItem(newItem, 'pysb.py')
    print "FILE UPDATE: " + str(newItem)
    
    # List file info from the newly created item
    ret = sb.getItemFileInfo(newItem)
    for fileinfo in ret:
        print "File " + fileinfo["name"] + ", " + str(fileinfo["size"]) + "bytes, download URL " + fileinfo["url"]
    
    # Download zip of files from the newly created item
    ret = sb.getItemFilesZip(newItem)
    print "Downloaded zip file " + str(ret)
    
    # Download all files attached to the item as individual files, and place them in the 
    # tmp directory under the current directory.
    path = "./tmp"
    if not os.path.exists(path):
        os.makedirs(path)
    ret = sb.getItemFiles(newItem, path)
    print "Downloaded files " + str(ret)
        
    # Delete the newly created item
    ret = sb.deleteSbItem(newItem)
    print "DELETE: " + str(ret)

    # Upload multiple files to create a new item
    ret = sb.uploadFilesAndCreateItem(sb.getMyItemsId(), ['pysb.py','readme.md'])
    print str(ret)
    
    # Search
    items = sb.findSbItemsByAnytext(username)
    while items and 'items' in items:
        for item in items['items']:
            print item['title']
        items = sb.next(items)

    # Logout
    sb.logout()

