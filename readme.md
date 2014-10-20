Python ScienceBase Utilities
============================
This Python module provides some basic services for interacting with ScienceBase.  It requires the "requests"
module to be installed, which can be found at http://docs.python-requests.org/en/latest/

Module Contents
---------------
The SbSession class provides the following methods:

### Login
* `login(username, password)`
Log into ScienceBase using the username and password.  This causes a cookie to be added to the session
to be used by subsequent calls.

* `loginc(username)`
Log into ScienceBase using the given username, and prompt for the password.  The password is not
echoed to the console.  Provided as a convenience for interactive scripts.

### Create
* `createSbItem(sbJson)`
Create a new ScienceBase item.  Documentation on the sbJson format can be found at
https://my.usgs.gov/confluence/display/sciencebase/ScienceBase+Item+Core+Model

### Read
* `getSbItem(id)`
Get the JSON for the ScienceBase item with the given ID.

* `getMyItemsId()`
Get the ID of the logged in user's "My Items"

* `get(url)`
Get the text response of the given URL.

* `getJson(url)`
Get the JSON response of the given URL.

* `getItemFilesZip(sbJson, destination)`
Get a zip of all files attached to the ScienceBase item and place it in the destination
folder.  Destination defaults to the current directory.  If specified, the destination folder 
must exist.  This creates the zip file server-side and then streams it to the client.

* `getItemFiles(sbJson, destination)`
Download all files attached to the ScienceBase item and place them in the destination folder.
Destination defaults to the current directory.  If specified, the destination folder must 
exist.  The files are streamed individually.

* `getItemFileInfo(sbJson)`
Get information about all files attached to a ScienceBase item.  Returns a list of 
dictionaries containing url, name and size of each file.

* `downloadFile(url, local_filename, destination)`
Download an individual file.  Destination defaults to the current directory.  If specified,
the destination folder must exist.

### Update
* `updateSbItem(sbJson)`
Updates an existing ScienceBase item.

* `uploadFileToItem(sbJson, filename)`
Upload a file to an existing ScienceBase item.

* `uploadFileAndCreateItem(parentid, filename)`
Upload a file and create a ScienceBase item.

* `uploadFilesAndCreateItem(sbJson, [filename,...])`
Upload a set of files and create a ScienceBase item.

### Delete
* `deleteSbItem(sbJson)`
Delete an existing ScienceBase item.

### Search
* `findSbItemsByAnytext(text)`
Find items containing the given text somewhere in the item.

* `findSbItemsByTitle(text)`
Find items containing the given text in the title of the item.

* `findSbItems(params)`
Find items meeting the criteria in the specified search parameters.  These are the same parameters that you pass
to ScienceBase in an advanced search.

* `next(items)`
Get the next page of results, where *items* is the current search results.

* `previous(items)`
Get the previous page of results, where *items* is the current search results.

Example Usage
-------------

````python
    import pysb
    import os
    
    sb = pysb.SbSession()

    # Get a public item.  No need to log in.
    itemJson = sb.getSbItem('505bc673e4b08c986b32bf81')
    print "Public Item: " + str(itemJson)

    # Get a private item.  Need to log in first.
    username = raw_input("Username:  ")
    sb.loginc(str(username))
    # Need to wait a bit after the login or errors can occur
    time.sleep(5)
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
````