#!/usr/bin/python
# requests is an optional library that can be found at http://docs.python-requests.org/en/latest/
from __future__ import print_function
try:
    # For Python 3.0 and later
    import http.client as httplib
    from urllib.request import urlopen
    from urllib.parse import urlencode
    import urllib.parse as urlparse
except ImportError:
    # Fall back to Python 2's urllib2
    import httplib
    from urllib import urlencode
    from urllib2 import urlopen
    import urlparse


import requests
import json
import os
import getpass
import logging
import mimetypes
from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound

class SbSession:
    _josso_url = None
    _base_sb_url = None
    _base_item_url = None
    _base_items_url = None
    _base_upload_file_url = None
    _base_upload_file_temp_url = None
    _base_download_files_url = None
    _base_move_item_url = None
    _base_undelete_item_url = None
    _base_shortcut_item_url = None
    _base_unlink_item_url = None
    _users_id = None
    _username = None
    _jossosessionid = None
    _session = None

    #
    # Initialize session and set JSON headers
    #
    def __init__(self, env=None):
        if env == 'beta':
            self._base_sb_url = "https://beta.sciencebase.gov/catalog/"
            self._josso_url = "https://my-beta.usgs.gov/josso/signon/usernamePasswordLogin.do"
            self._users_id = "4f4e4772e4b07f02db47e231"
        elif env == 'dev':
            self._base_sb_url = "http://localhost:8090/catalog/"
            self._josso_url = "https://my-beta.usgs.gov/josso/signon/usernamePasswordLogin.do"
        else:
            self._base_sb_url = "https://www.sciencebase.gov/catalog/"
            self._josso_url = "https://my.usgs.gov/josso/signon/usernamePasswordLogin.do"
            self._users_id = "4f4e4772e4b07f02db47e231"

        self._base_item_url = self._base_sb_url + "item/"
        self._base_items_url = self._base_sb_url + "items/"
        self._base_upload_file_url = self._base_sb_url + "file/uploadAndUpsertItem/"
        self._base_download_files_url = self._base_sb_url + "file/get/"
        self._base_upload_file_temp_url = self._base_sb_url + "file/upload/"
        self._base_move_item_url = self._base_items_url + "move/"
        self._base_undelete_item_url = self._base_item_url + "undelete/"
        self._base_shortcut_item_url = self._base_items_url + "addLink/"
        self._base_unlink_item_url = self._base_items_url + "unlink/"

        self._session = requests.Session()
        self._session.headers.update({'Accept': 'application/json'})
        pysb_agent = ' sciencebase-pysb'
        try:
            pysb_agent += '/%s' % get_distribution("pysb").version
        except DistributionNotFound:
            pass
        self._session.headers.update({'User-Agent': self._session.headers['User-Agent'] + pysb_agent})

    #
    # Log into ScienceBase
    #
    def login(self, username, password):
        # Save username
        self._username = username

        # Login and save JOSSO Session ID
        self._session.post(self._josso_url, params={'josso_cmd': 'josso', 'josso_username':username, 'josso_password':password})
        if ('JOSSO_SESSIONID' not in self._session.cookies):
            raise Exception("Login failed")
        self._jossosessionid = self._session.cookies['JOSSO_SESSIONID']
        self._session.params = {'josso':self._jossosessionid}

        return self

    #
    # Log out of ScienceBase
    #
    def logout(self):
        self._session.post(self._base_sb_url + 'j_spring_security_logout')
        self._session.cookies.clear_session_cookies()
        self._session.params = {}

    #
    # Log into ScienceBase, prompting for the password
    #
    def loginc(self, username):
        tries = 0
        while (tries < 5):
            password = getpass.getpass()
            try:
                return self.login(username, password)
            except Exception:
                tries += 1
                print("Invalid password, try again")
        raise Exception("Too many invalid password attemps, you may need to wait 15 minutes before trying again")

    #
    # Return whether the SbSession is logged in and active in ScienceBase
    #
    def is_logged_in(self):
        return self.get_session_info()['isLoggedIn']

    #
    # Ping ScienceBase.  A very low-cost operation to determine whether ScienceBase is available
    #
    def ping(self):
        return self.get_json(self._base_item_url + 'ping')

    #
    # Return ScienceBase Josso session info
    #
    def get_session_info(self):
        return self.get_json(self._base_sb_url + 'jossoHelper/sessionInfo?includeJossoSessionId=true')

    #
    # Get the ScienceBase Item JSON with the given ID
    #
    # Returns JSON for the ScienceBase Item with the given ID
    #
    def get_item(self, itemid):
        ret = self._session.get(self._base_item_url + itemid)
        return self._get_json(ret)

    #
    # Create a new Item in ScienceBase
    #
    def create_item(self, item_json):
        ret = self._session.post(self._base_item_url, data=json.dumps(item_json))
        return self._get_json(ret)

    #
    # Update an existing ScienceBase Item
    #
    def update_item(self, item_json):
        ret = self._session.put(self._base_item_url + item_json['id'], data=json.dumps(item_json))
        return self._get_json(ret)

    #
    # Update multiple ScienceBase items (takes an array of items)
    #
    def update_items(self, items_json):
        ret = self._session.put(self._base_items_url, data=json.dumps(items_json))
        return self._get_json(ret)

    #
    # Delete an existing ScienceBase Item
    #
    def delete_item(self, item_json):
        ret = self._session.delete(self._base_item_url + item_json['id'], data=json.dumps(item_json))
        self._check_errors(ret)
        return True

    #
    # Undelete a ScienceBase Item
    #
    def undelete_item(self, itemid):
        ret = self._session.post(self._base_undelete_item_url, params={'itemId': itemid})
        self._check_errors(ret)
        return self._get_json(ret)


    #
    # Delete multiple ScienceBase Items.  This is much more
    # efficient than using delete_item() for mass deletions, as it performs it server-side
    # in one call to ScienceBase.
    #
    def delete_items(self, itemIds):
        ids_json = []
        for itemId in itemIds:
            ids_json.append({'id': itemId})
        ret = self._session.delete(self._base_items_url, data=json.dumps(ids_json))
        self._check_errors(ret)
        return True

    #
    # Move an existing ScienceBase Item under a new parent
    #
    def move_item(self, itemid, parentid):
        ret = self._session.post(self._base_move_item_url, params={'itemId': itemid, 'destId': parentid})
        self._check_errors(ret)
        return self._get_json(ret)

    #
    # Move ScienceBase Items under a new parent
    #
    def move_items(self, itemids, parentid):
        count = 0
        if itemids:
            for itemid in itemids:
                print('moving ' + itemid)
                self.move_item(itemid, parentid)
                count += 1
        return count

    #
    # Upload a file to an existing Item in ScienceBase
    #
    def upload_file_to_item(self, item, filename):
        return self.upload_files_and_update_item(item, [filename])

    #
    # Upload a file and create a new Item in ScienceBase
    #
    def upload_file_and_create_item(self, parentid, filename):
        return self.upload_files_and_create_item(parentid, [filename])

    #
    # Upload multiple files and create a new Item in ScienceBase
    #
    def upload_files_and_create_item(self, parentid, filenames):
        url = self._base_upload_file_url
        files = []
        for filename in filenames:
            if (os.access(filename, os.F_OK)):
                files.append(('file', open(filename, 'rb')))
            else:
                raise Exception("File not found: " + filename)
        ret = self._session.post(url, files=files, params={'parentId': parentid})
        return self._get_json(ret)

    #
    # Upload multiple files and update an existing Item in ScienceBase
    #
    def upload_files_and_update_item(self, item, filenames):
        return self.upload_files_and_upsert_item(item, filenames)

    #
    # Upload multiple files and create or update an Item in ScienceBase
    #
    def upload_files_and_upsert_item(self, item, filenames):
        url = self._base_upload_file_url
        files = []
        for filename in filenames:
            if (os.access(filename, os.F_OK)):
                files.append(('file', open(filename, 'rb')))
            else:
                raise Exception("File not found: " + filename)
        data = {'item': json.dumps(item)}
        if 'id' in item and item['id']:
            data['id'] = item['id']
        ret = self._session.post(url, files=files, data=data)
        return self._get_json(ret)

    #
    # Upload a file to ScienceBase.  The file will be staged in a temporary area.  In order
    # to attach it to an Item, the pathOnDisk must be added to an Item files entry, or
    # one of a facet's file entries.
    #
    def upload_file(self, filename, mimetype=None):
        retval = None
        url = self._base_upload_file_temp_url

        if (os.access(filename, os.F_OK)):
            #
            # if no mimetype was sent in, try to guess
            #
            if None == mimetype:
                mimetype = mimetypes.guess_type(filename)
            (path, fname) = os.path.split(filename)
            ret = self._session.post(url, files=[('files[]', (fname, open(filename, 'rb'), mimetype))])
            retval = self._get_json(ret)
        else:
            raise Exception("File not found: " + filename)
        return retval

    #
    # Replace a file on a ScienceBase Item.  This method will replace all files named
    # the same as the new file, whether they are in the files list or on a facet.
    #
    def replace_file(self, filename, item):
        (path, fname) = os.path.split(filename)
        #
        # replace file in files list
        #
        if 'files' in item:
            new_files = []
            for f in item['files']:
                if f['name'] == fname:
                    f = self._replace_file(filename, f)
                new_files.append(f)
            item['files'] = new_files
        #
        # replace file in facets
        #
        if 'facets' in item:
            new_facets=[]
            for facet in item['facets']:
                if 'files' in facet:
                    new_files = []
                    for f in facet['files']:
                        if f['name'] == fname:
                            f = self._replace_file(filename, f)
                        new_files.append(f)
                    facet['files'] = new_files
                    new_facets.append(facet)
            item['facets'] = new_facets
        self.update_item(item)

    #
    # Upload a file to ScienceBase and update file json with new path on disk.
    #
    def _replace_file(self, filename, itemfile):
        #
        # Upload file and point file JSON at it
        #
        upld_json = self.upload_file(filename, itemfile['contentType'])
        itemfile['pathOnDisk'] = upld_json[0]['fileKey']
        itemfile['dateUploaded'] = upld_json[0]['dateUploaded']
        itemfile['uploadedBy'] = upld_json[0]['uploadedBy']
        return itemfile

    #
    # Download all files from a ScienceBase Item as a zip.  The zip is created server-side
    # and streamed to the client.
    #
    def get_item_files_zip(self, item, destination='.'):
        #
        # First check that there are files attached to the item, otherwise the call
        # to ScienceBase will return an empty zip file
        #
        file_info = self.get_item_file_info(item)
        if not file_info:
            return None

        #
        # Download the zip
        #
        r = self._session.get(self._base_download_files_url + item['id'], stream=True)
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
    def get_item_file_info(self, item):
        retval = []
        if item:
            #
            # regular files
            #
            if 'files' in item:
                for f in item['files']:
                    finfo = {}
                    if 'url' in f:
                        finfo['url'] = f['url']
                    if 'name' in f:
                        finfo['name'] = f['name']
                    if 'size' in f:
                        finfo['size'] = f['size']
                    retval.append(finfo)
            if 'facets' in item:
                for facet in item['facets']:
                    if 'files' in facet:
                        for f in facet['files']:
                            finfo = {}
                            if 'url' in f:
                                finfo['url'] = f['url']
                            if 'name' in f:
                                finfo['name'] = f['name']
                            if 'size' in f:
                                finfo['size'] = f['size']
                            retval.append(finfo)
        return retval

    #
    # Download file from URL
    #
    def download_file(self, url, local_filename, destination='.'):
        complete_name = os.path.join(destination, local_filename)
        print("downloading " + url + " to " + complete_name)
        r = self._session.get(url, stream=True)

        with open(complete_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return complete_name

    #
    # Download the individual files attached to a ScienceBase Item
    #
    def get_item_files(self, item, destination='.'):
        file_info = self.get_item_file_info(item)
        for file_info in file_info:
            self.download_file(file_info['url'], file_info['name'], destination)
        return file_info

    #
    # Get the ID of the logged-in user's My Items
    #
    def get_my_items_id(self):
        if (self._username):
            params = {'q': '', 'lq': 'title.untouched:"' + self._username + '"'}
            if self._users_id:
                params['parentId'] = self._users_id
            items = self.find_items(params)
            if ('items' in items):
                for item in items['items']:
                    if (item['title'] == self._username):
                        return item['id']

    #
    # Get IDs of all children for a given parent
    #
    def get_child_ids(self, parentid):
        retval = []
        items = self.find_items({'filter':'parentIdExcludingLinks=' + parentid})
        while items and 'items' in items:
            for item in items['items']:
                retval.append(item['id'])
            items = self.next(items)
        return retval

    #
    # Get IDs of all shortcutted items for a given item
    #
    def get_shortcut_ids(self, itemid):
        retval = []
        items = self.find_items({'filter':'linkParentId=' + itemid})
        while items and 'items' in items:
            for item in items['items']:
                retval.append(item['id'])
            items = self.next(items)
        return retval

    #
    # Create a shortcut to another item
    #
    def create_shortcut(self, itemid, parentid):
        ret = self._session.post(self._base_shortcut_item_url, params={'itemId':itemid, 'destId':parentid})
        return self._get_json(ret)

    #
    # Remove a shortcut to another item
    #
    def remove_shortcut(self, itemid, parentid):
        ret = self._session.post(self._base_unlink_item_url, params={'itemId':itemid, 'destId':parentid})
        return self._get_json(ret)

    #
    # WORK IN PROGRESS
    # Given an OPEeNDAP URL, create a NetCDFOPeNDAP facet from the return data
    #
    def get_NetCDFOPeNDAP_info_facet(self, url):
        data = self._get_json(self._session.post(self._base_sb_url + 'items/scrapeNetCDFOPeNDAP', params={'url': url}))
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
    def find_items(self, params):
        return self._get_json(self._session.get(self._base_items_url, params=params))

    #
    # Get the next set of items from the search
    #
    def next(self, items):
        ret_val = None
        if 'nextlink' in items:
            ret_val = self._get_json(self._session.get(self._remove_josso_param(items['nextlink']['url'])))
        return ret_val

    #
    # Get the previous set of items from the search
    #
    def previous(self, items):
        ret_val = None
        if 'prevlink' in items:
            ret_val = self._get_json(self._session.get(self._remove_josso_param(items['prevlink']['url'])))
        return ret_val

    #
    # Search for ScienceBase items by free text
    #
    def find_items_by_any_text(self, text):
        return self.find_items({'q': text})

    #
    # Search for ScienceBase items by title
    #
    def find_items_by_title(self, text):
        return self.find_items({'q': '', 'lq': 'title:"' + text + '"'})

    #
    # Get the text response of the given URL
    #
    def get(self, url):
        return self._get_text(self._session.get(url))

    #
    # Get the JSON response of the given URL
    #
    def get_json(self, url):
        return self._get_json(self._session.get(url))

    #
    # Check the status code of the response, and return the JSON
    #
    def _get_json(self, response):
        self._check_errors(response)
        try:
            return response.json()
        except:
            raise Exception("Error parsing JSON response")

    #
    # Check the status code of the response, and return the text
    #
    def _get_text(self, response):
        self._check_errors(response)
        try:
            return response.text
        except:
            raise Exception("Error parsing response")

    #
    # Check the status code of the response
    #
    def _check_errors(self, response):
        if (response.status_code == 404):
            raise Exception("Resource not found, or user does not have access")
        elif (response.status_code == 401):
            raise Exception("Unauthorized access")
        elif (response.status_code != 200):
            raise Exception("Other HTTP error: " + str(response.status_code) + ": " + response.text)

    #
    # Remove josso parameter from URL
    #
    def _remove_josso_param(self, url):
        o = urlparse.urlsplit(url)
        q = [x for x in urlparse.parse_qsl(o.query) if "josso" not in x]
        return urlparse.urlunsplit((o.scheme, o.netloc, o.path, urlencode(q), o.fragment))

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
    # Backwards compatibility section.  May be removed in future releases.
    #
    def isLoggedIn(self):
        return self.is_logged_in()
    def getSessionInfo(self):
        return self.get_session_info()
    def getSbItem(self, item_id):
        return self.get_item(item_id)
    def createSbItem(self, item_json):
        return self.create_item(item_json)
    def updateSbItem(self, item_json):
        return self.update_item(item_json)
    def deleteSbItem(self, item_json):
        return self.delete_item(item_json)
    def undeleteSbItem(self, item_id):
        return self.undelete_item(item_id)
    def deleteSbItems(self, item_ids):
        return self.delete_items(item_ids)
    def moveSbItem(self, item_id, parent_id):
        return self.move_item(item_id, parent_id)
    def moveSbItems(self, item_ids, parent_id):
        return self.move_items(item_ids, parent_id)
    def uploadFileToItem(self, item, filename):
        return self.upload_file_to_item(item, filename)
    def uploadFileAndCreateItem(self, parent_id, filename):
        return self.upload_file_and_create_item(parent_id, filename)
    def uploadFilesAndCreateItem(self, parent_id, filenames):
        return self.upload_files_and_create_item(parent_id, filenames)
    def uploadFilesAndUpdateItem(self, item, filenames):
        return self.upload_files_and_update_item(item, filenames)
    def uploadFilesAndUpsertItem(self, item, filenames):
        return self.upload_files_and_upsert_item(item, filenames)
    def uploadFile(self, filename, mimetype=None):
        return self.upload_file(filename, mimetype)
    def replaceFile(self, filename, item):
        return self.replace_file(filename, item)
    def getItemFilesZip(self, item, destination='.'):
        return self.get_item_files_zip(item, destination)
    def getItemFileInfo(self, item):
        return self.get_item_file_info(item)
    def downloadFile(self, url, local_filename, destination='.'):
        return self.download_file(url, local_filename, destination)
    def getItemFiles(self, item, destination='.'):
        return self.get_item_files(item, destination)
    def getMyItemsId(self):
        return self.get_my_items_id()
    def getChildIds(self, parent_id):
        return self.get_child_ids(parent_id)
    def getNetCDFOPeNDAPInfoFacet(self, url):
        return self.get_NetCDFOPeNDAP_info_facet(url)
    def findSbItems(self, params):
        return self.find_items(params)
    def findSbItemsByAnytext(self, text):
        return self.find_items_by_any_text(text)
    def findSbItemsByTitle(self, text):
        return self.find_items_by_title(text)
    def getJson(self, response):
        return self.get_json(response)
