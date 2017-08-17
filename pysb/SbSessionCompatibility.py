"""This Python module provides backwards-compatibility for old scripts using the original camel case
method names of pysb.
"""
from pysb import SbSession

class SbSessionCompatibility:
    """SbSessionCompatibility encapsulates a session with ScienceBase, and provides methods for working
    with ScienceBase Catalog Items. Import this class instead of SbSession, and change the creation
    of the session to be `sb = SbSessionCompatibility()`.
    """
    _sb = None

    def __init__(self, env=None):
        self._sb = SbSession(env)

    def login(self, username, password):
        """Log into ScienceBase

        :param username: The ScienceBase user to log in as
        :param password: The ScienceBase password for the given user
        :return: The SbSession object with the user logged in
        """
        self._sb.login(username, password)
        return self

    def loginc(self, username):
        """Log into ScienceBase, prompting for the password

        :param username: The ScienceBase user to log in as
        :return: The SbSession object with the user logged in
        """
        self._sb.loginc(username)
        return self

    def ping(self):
        """Ping ScienceBase.  A very low-cost operation to determine whether ScienceBase is available.
        
        :return: JSON response from ScienceBase Catalog
        """
        return self._sb.ping()

    def isLoggedIn(self):
        """Determine whether the SbSession is logged in and active in ScienceBase
        
        :return: Whether the SbSession is logged in and active in ScienceBase.
        """
        return self._sb.is_logged_in()

    def getSessionInfo(self):
        """Get the JOSSO session information for the current session

        :return: ScienceBase Josso session info
        """
        return self._sb.get_session_info()

    def getSbItem(self, item_id):
        """Get the ScienceBase Item JSON with the given ID
        
        :param params: Allows you to specify query params, such as {'fields':'title,ancestors'} for ?fields=title,ancestors
        :return: JSON for the ScienceBase Item with the given ID
        """
        return self._sb.get_item(item_id)

    def createSbItem(self, item_json):
        """Create a new Item in ScienceBase

        :param item_json: JSON representing the ScienceBase Catalog item to create
        :return: Full item JSON from ScienceBase Catalog after creation
        """
        return self._sb.create_item(item_json)

    def updateSbItem(self, item_json):
        """Update an existing ScienceBase Item

        :param item_json: JSON representing the ScienceBase Catalog item to update
        :return: Full item JSON from ScienceBase Catalog after update
        """
        return self._sb.update_item(item_json)

    def deleteSbItem(self, item_json):
        """Delete an existing ScienceBase Item

        :param item_json: JSON representing the ScienceBase Catalog item to delete
        :return
        """
        return self._sb.delete_item(item_json)

    def undeleteSbItem(self, item_id):
        """Undelete a ScienceBase Item
        :param itemid: ID of the Item to undelete
        :return: JSON of the undeleted Item
        """
        return self._sb.undelete_item(item_id)

    def deleteSbItems(self, item_ids):
        """Delete multiple ScienceBase Items.  This is much more efficient than using delete_item() for mass
        deletions, as it performs it server-side in one call to ScienceBase.
        
        :param itemIds: List of Item IDs to delete
        :return: True if the items were successfully deleted
        """
        return self._sb.delete_items(item_ids)

    def moveSbItem(self, item_id, parent_id):
        """Move an existing ScienceBase Item under a new parent

        :param itemid: ID of the Item to move
        :param parentid: ID of the new parent Item
        :return
        """
        return self._sb.move_item(item_id, parent_id)

    def moveSbItems(self, item_ids, parent_id):
        """Move ScienceBase Items under a new parent

        :param itemids: A list of ScienceBase Catalog Item IDs of the Items to move
        :param parentid: ScienceBase Catalog Item ID of the new parent Item
        :return: A count of the number of Items moved
        """
        return self._sb.move_items(item_ids, parent_id)

    def uploadFileToItem(self, item, filename):
        """Upload a file to an existing Item in ScienceBase

        :param item:
        :param filename: Filenames of the file to upload
        :param scrape_file: Whether to scrape metadata and create extensions from special files
        :return
        """
        return self._sb.upload_file_to_item(item, filename)

    def uploadFileAndCreateItem(self, parent_id, filename):
        """Upload a file and create a new Item in ScienceBase

        :param parentid: ScienceBase Catalog Item JSON of the Item under which to create the new Item
        :param filename: Filename of the file to upload
        :param scrape_file: Whether to scrape metadata and create extensions from special files
        :return: The ScienceBase Catalog Item JSON of the new Item
        """
        return self._sb.upload_file_and_create_item(parent_id, filename)

    def uploadFilesAndCreateItem(self, parent_id, filenames):
        """Upload multiple files and create a new Item in ScienceBase

        :param parentid: ScienceBase Catalog Item JSON of the Item under which to create the new Item
        :param filenames: Filename of the files to upload
        :param scrape_file: Whether to scrape metadata and create extensions from special files
        :return: ScienceBase Catalog Item JSON of the new Item
        """
        return self._sb.upload_files_and_create_item(parent_id, filenames)
 
    def uploadFilesAndUpdateItem(self, item, filenames):
        """Upload multiple files and update an existing Item in ScienceBase

        :param item: ScienceBase Catalog Item JSON of the Item to update
        :param filenames: Filenames of the files to upload
        :param scrape_file: Whether to scrape metadata and create extensions from special files
        :return: The ScienceBase Catalog Item JSON of the updated Item
        """
        return self._sb.upload_files_and_update_item(item, filenames)

    def uploadFilesAndUpsertItem(self, item, filenames):
        """Upload multiple files and create or update an Item in ScienceBase

        :param item: ScienceBase Catalog Item JSON of the Item to update
        :param filenames: Filenames of the files to upload
        :param scrape_file: Whether to scrape metadata and create extensions from special files
        :return: The ScienceBase Catalog Item JSON of the updated Item
        """
        return self._sb.upload_files_and_upsert_item(item, filenames)

    def uploadFile(self, filename, mimetype=None):
        """ADVANCED USE -- USE OTHER UPLOAD METHODS IF AT ALL POSSIBLE. Upload a file to ScienceBase.  The file will
        be staged in a temporary area.  In order to attach it to an Item, the pathOnDisk must be added to an Item
        files entry, or one of a facet's file entries.

        :param filename: File to upload
        :param mimetype: MIME type of the file
        :return: JSON response from ScienceBase
        """
        return self._sb.upload_file(filename, mimetype)

    def replaceFile(self, filename, item):
        """Replace a file on a ScienceBase Item.  This method will replace all files named
        the same as the new file, whether they are in the files list or on a facet.

        :param filename: Name of the file to replace
        :param item: ScienceBase Catalog Item JSON of the Item on which to replace the file
        :return: ScienceBase Catalog Item JSON of the updated Item
        """
        return self._sb.replace_file(filename, item)

    def getItemFilesZip(self, item, destination='.'):
        """Download all files from a ScienceBase Item as a zip.  The zip is created server-side
        and streamed to the client.

        :param item: ScienceBase Catalog Item JSON of the item from which to download files
        :param destination:  Destination directory in which to store the zip file
        :return: The full name and path of the downloaded file
        """
        return self._sb.get_item_files_zip(item, destination)

    def getItemFileInfo(self, item):
        """Retrieve file information from a ScienceBase Item

        :param item: ScienceBase Catalog Item JSON of the item from which to get file information
        :return: A list of dictionaries containing url, name and size of each file

        """
        return self._sb.get_item_file_info(item)

    def downloadFile(self, url, local_filename, destination='.'):
        """Download file from URL

        :param url: ScienceBase Catalog Item file download URL
        :param local_filename: Name to use for the local file
        :param destination: Destination directory in which to store the files
        :return: The full name and path of the downloaded file
        """
        return self._sb.download_file(url, local_filename, destination)

    def getItemFiles(self, item, destination='.'):
        """Download the individual files attached to a ScienceBase Item

        :param item: ScienceBase Catalog Item JSON of the item from which to download files
        :param destination: Destination directory in which to store the files
        :return: The ScienceBase Catalog file info JSON response
        """
        return self._sb.get_item_files(item, destination)

    def getMyItemsId(self):
        """Get the ID of the logged-in user's My Items

        :return: The ScienceBase Catalog Item ID of the logged in user's My Items folder
        """
        return self._sb.get_my_items_id()

    def getChildIds(self, parent_id):
        """Get IDs of all immediate children for a given parent

        :param parentid: ScienceBase Catalog Item ID of the item for which to look for children
        :return: A List of ScienceBase Catalog Item IDs of the direct children
        """
        return self._sb.get_child_ids(parent_id)

    def getNetCDFOPeNDAPInfoFacet(self, url):
        """Given an OPeNDAP URL, create a NetCDFOPeNDAP facet from the return data

        :param url: OPeNDAP URL to query
        :return: ScienceBase Catalog Item facet JSON with information on the OPeNDAP service
        """
        return self._sb.get_NetCDFOPeNDAP_info_facet(url)

    def findSbItems(self, params):
        """Search for ScienceBase items

        :param params: ScienceBase Catalog search parameters
        :return: ScienceBase Catalog search response object containing the next page of results for the search
        """
        return self._sb.find_items(params)

    def findSbItemsByAnytext(self, text):
        """Search for ScienceBase items by free text

        :param text: Text to search for in all searchable fields of ScienceBase Catalog Items
        :return: ScienceBase Catalog search response containing results
        """
        return self._sb.find_items_by_any_text(text)

    def findSbItemsByTitle(self, text):
        """Search for ScienceBase items by title

        :param text: Text to search for in the title field
        :return: ScienceBase Catalog search response containing results
        """
        return self._sb.find_items_by_title(text)

    def getJson(self, response):
        """Get the JSON response of the given URL

        :param url: URL to request via HTTP GET
        :return: JSON response
        """
        return self._sb.get_json(response)

    def next(self, items):
        """Get the next set of items from the search

        :param items: ScienceBase Catalog search response object from a prior search
        :return: ScienceBase Catalog search response object containing the next page of results for the search
        """
        return self._sb.next(items)

    def previous(self, items):
        """Get the previous set of items from the search

        :param items: ScienceBase Catalog search response object from a prior search
        :return: ScienceBase Catalog search response object containing the previous page of results for the search
        """
        return self._sb.previous(items)

    def get(self, url):
        """Get the text response of the given URL

        :param url: URL to request via HTTP GET
        :return: TEXT response
        """
        return self._sb.get(url)

    def debug(self):
        """Turn on HTTP logging for debugging purposes.
        This enables debugging at httplib level (requests->urllib3->httplib)
        You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
        The only thing missing will be the response.body which is not logged.
        """
        self._sb.debug()
