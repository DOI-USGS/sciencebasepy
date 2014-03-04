Python ScienceBase Utilities
============================
This Python module provides some basic services for interacting with ScienceBase.  It requires the "requests"
module to be installed, which can be found at http://docs.python-requests.org/en/latest/

Module Contents
---------------
The SbSession class provides the following methods:

* login(username, password)
Log into ScienceBase using the username and password.  This causes a cookie to be added to the session
to be used by subsequent calls.

* loginc(username)
Log into ScienceBase using the given username, and prompt for the password.  The password is not
echoed to the console.  Provided as a convenience for interactive scripts.

* getSbItem(id)
Get the JSON for the ScienceBase item with the given ID.

* createSbItem(sbJson)
Create a new ScienceBase item.  Documentation on the sbJson format can be found at
https://my.usgs.gov/confluence/display/sciencebase/ScienceBase+Item+Core+Model

* uploadFileToItem(sbJson, filename)
Upload a file to an existing ScienceBase item.

* getMyItemsId()
Get the ID of the logged in user's "My Items"

Example Usage
-------------
````python
import pysb

# Create the ScienceBase session
sb = pysb.SbSession()

# Get a public item.  No need to log in.
itemJson = sb.getSbItem('505bc673e4b08c986b32bf81')

# Get a private item.  Need to log in first.
sb.loginc(str(raw_input("Username:  ")))
itemJson = sb.getSbItem(sb.getMyItemsId())

# Create a new item.  The minimum required is a title for the new item, and the parent ID.
newItem = {'title': 'This is a new test item',
        'parentId': sb.getMyItemsId(),
        'provenance': {'annotation': 'Python ScienceBase REST test script'}}
newItem = sb.createSbItem(newItem)

# Upload a file to the newly created item
sb.uploadFileToItem(newItem, 'pysb.py')
````