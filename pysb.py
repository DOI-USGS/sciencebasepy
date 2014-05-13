#!/usr/bin/python
# requests is an optional library that can be found at http://docs.python-requests.org/en/latest/
import requests
import json
import os
import getpass
import logging
import httplib

class SbSession:
    _jossoURL = None
    _baseSbURL = None
    _baseItemURL = None
    _baseItemsURL = None
    _baseUploadFileURL = None
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
        elif env == 'dev':
            self._baseSbURL = "http://localhost:8090/catalog/"
            self._jossoURL = "https://my-beta.usgs.gov/josso/signon/usernamePasswordLogin.do"
        else:
            self._baseSbURL = "https://www.sciencebase.gov/catalog/"
            self._jossoURL = "https://my.usgs.gov/josso/signon/usernamePasswordLogin.do"

        self._baseItemURL = self._baseSbURL + "item/"
        self._baseItemsURL = self._baseSbURL + "items/"
        self._baseUploadFileURL = self._baseSbURL + 'file/uploadAndUpsertItem/'

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
    # Log into ScienceBase, prompting for the password
    #
    def loginc(self, username):
        password = getpass.getpass()
        return self.login(username, password)

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
    # Upload a file to an existing Item in ScienceBase
    #
    def uploadFileToItem(self, item, filename):
        retval = None
        url = self._baseUploadFileURL
        if (os.access(filename, os.F_OK)):
            files = {'file': open(filename, 'rb')}
            ret = self._session.post(url, files=files, params={'id': item['id'], 'item': json.dumps(item)})
            retval = self._getJson(ret)
        else:
            raise Exception("File not found: " + filename)
        return retval

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
    # Upload a file and create a new Item in ScienceBase
    #
    def uploadFileAndCreateItem(self, parentid, filename):
        retval = None
        url = self._baseUploadFileURL
        if (os.access(filename, os.F_OK)):
            files = {'file': open(filename, 'rb')}
            ret = self._session.post(url, files=files, params={'parentId': parentid})
            retval = self._getJson(ret)
        else:
            raise Exception("File not found: " + filename)
        return retval

    #
    # Get the ID of the logged-in user's My Items
    #
    def getMyItemsId(self):    
        if (self._username):
            items = self.findSbItemsByTitle(self._username)
            if ('items' in items): 
                for item in items['items']:
                    if (item['title'] == self._username):
                        return item['id']

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
            retVal = self._getJson(self._session.get(items['nextlink']['url']))
        return retVal

    #
    # Get the previous set of items from the search
    #
    def previous(self, items):
        retVal = None
        if 'prevlink' in items:
            retVal = self._getJson(self._session.get(items['prevlink']['url']))
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
            raise Exception("Other HTTP error: " + str(response.status_code))
        
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
    sb.loginc(str(raw_input("Username:  ")))
    itemJson = sb.getSbItem(sb.getMyItemsId())
    print "My Items: " + str(itemJson)

    # Create a new item.  The minimum required is a title for the new item, and the parent ID
    newItem = {'title': 'This is a new test item',
        'parentId': sb.getMyItemsId(),
        'provenance': {'annotation': 'Python ScienceBase REST test script'}}
    newItem = sb.createSbItem(newItem)
    print "NEW ITEM: " + str(newItem)

    # Upload a file to the newly created item
    ret = sb.uploadFileToItem(newItem, 'pysb.py')
    print "FILE UPDATE: " + str(ret)

    # Upload multiple files to create a new item
    ret = sb.uploadFilesAndCreateItem(sb.getMyItemsId(), ['pysb.py','readme.md'])
    print str(ret)

    # Search
    items = sb.findSbItemsByAnytext('test')
    while items and 'items' in items:
        for item in items['items']:
            print item['title']
        items = sb.next(items)

