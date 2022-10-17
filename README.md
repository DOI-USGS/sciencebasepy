Python ScienceBase Utilities
============================
This Python module provides some basic services for interacting with ScienceBase.  It requires the "requests"
module to be installed, which can be found at
[http://docs.python-requests.org/en/latest/](http://docs.python-requests.org/en/latest/).
If you get security errors also install requests[security]

As of version 2.0.0, Python 2.x is no longer supported.

Quick Start
-----------
sciencebasepy can be installed with pip:
    
    `pip install sciencebasepy`

Otherwise, download the contents of this repository, and install the sciencebasepy libraries into 
your python installation by running `python setup.py install`.  Example usage is contained 
in `demo.py`.

There are several iPython notebooks in this repository with example code. For more in-depth information and 
examples on searching, see 
[Searching ScienceBase with ScienceBasePy.ipynb](https://github.com/usgs/sciencebasepy/blob/master/Searching%20ScienceBase%20with%20ScienceBasePy.ipynb).
For batch processing, see 
[Batch Processing.ipynb](https://github.com/usgs/sciencebasepy/blob/master/Batch%20Processing.ipynb).

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

* `is_logged_in()`
Return whether the SbSession is logged in and active in ScienceBase

* `get_session_info()`
Return ScienceBase Josso session info

* `ping()`
Ping ScienceBase.  A very low-cost operation to determine whether ScienceBase is available.

* `logout()`
Log out of ScienceBase

### Create
Note: When uploading associated files, such as the various files making up a shapefile, or a 
raster and its associated SLD, be sure to upload them with a single call to 
`upload_files_and_create_item`. Otherwise, ScienceBase will not create the appropriate facets, 
and services will not be created.

* `create_item(item_dict)`
Create a new ScienceBase item.  Documentation on the sbJSON format can be found at
https://my.usgs.gov/confluence/display/sciencebase/ScienceBase+Item+Core+Model

* `create_items(item_dict_list)`
Create multiple new Items in ScienceBase. item_dict_list: list of item_dict objects representing the ScienceBase Catalog items to create.

* `create_hidden_property(item_id, item_dict)`
Create a new Hidden Property for a Sciencebase item : POST /catalog/item/<item_id>/hiddenProperties
Documentation of the json can be found at https://code.chs.usgs.gov/sciencebase/dev-docs/wikis/APIs/Catalog/Item-Hidden-Properties

* `upload_file_and_create_item(parent_id, filename)`
Upload a file and create a ScienceBase item. Add the parameter `scrape_file=False` to bypass ScienceBase metadata
processing.

* `upload_files_and_create_item(parent_id, [filename,...])`
Upload a set of files and create a ScienceBase item. Add the parameter `scrape_file=False` to bypass ScienceBase
metadata processing.

### Read
* `get_item(id, params)`
Get the JSON for the ScienceBase item with the given ID.  
params argument is optional and allows you to specify query params, so params={'fields':'title,ancestors'} is for ?fields=title,ancestors 
similar to find_items.

* `get_my_items_id()`
Get the ID of the logged in user's "My Items"

* `get_hidden_properties(item_id)`
List All Hidden Properties for a given Item: GET /catalog/item/<item_id>/hiddenProperties

* `get_hidden_property(item_id, hiddenpropertyid)`
Get a specific Hidden Property for a given Item : GET /catalog/item/<item_id>/hiddenProperties/<ID>

* `get_item_ids_by_hidden_property(hidden_property)`
Get the ScienceBase IDs of Items associated with the given hidden property. Hidden property JSON
(for the hidden_property parameter) contains two fields, "type" and "value" both of which are
optional.

* `get_child_ids(parent_id)`
Get the IDs of all immediate children of the ScienceBase item with the given ID (does not follow shortcuts).

* `get_ancestor_ids(parent_id)`
Get IDs of all descendants of given item excluding those which are linked in (short-cutted). 
(That is, this finds items by ancestorsExcludingLinks=<parent_id> and builds a list of their IDs).

* `get(url)`
Get the text response of the given URL.

* `get_json(url)`
Get the JSON response of the given URL.

* `get_item_files_zip(item_dict, destination)`
Get a zip of all files attached to the ScienceBase item and place it in the destination
folder.  Destination defaults to the current directory.  If specified, the destination folder
must exist.  This creates the zip file server-side and then streams it to the client.

* `get_item_files(item_dict, destination)`
Download all files attached to the ScienceBase item and place them in the destination folder.
Destination defaults to the current directory.  If specified, the destination folder must
exist.  The files are streamed individually.

* `get_item_file_info(item_dict)`
Get information about all files attached to a ScienceBase item.  Returns a list of
dictionaries containing url, name and size of each file.

* `download_file(url, local_filename, destination)`
Download an individual file.  Destination defaults to the current directory.  If specified,
the destination folder must exist.

* `generate_S3_download_links(itemid, filenames)`
Generates a list of tokenized S3 download links for files in the ScienceBase S3 standard bucket or public bucket (does not work for on-premise files).

* `download_cloud_files(filenames, download_links, destination)`
Downloads a list of ScienceBase S3 files using tokenized S3 download links.  Destination defaults to the current directory.  If specified, the destination folder must exist.

### Update
Note: When uploading associated files, such as the various files making up a shapefile, or a 
raster and its associated SLD, be sure to upload them with a single call to one of the `upload_files*` methods.
Otherwise, ScienceBase will not create the appropriate facets, and services will not be created.

* `update_item(item_dict)`
Updates an existing ScienceBase item.

* `update_items(item_dict_list)`
Update multiple Items in ScienceBase. item_dict_list: list of item_dict objects representing the ScienceBase Catalog items to update.

* `update_hidden_property(item_id, hiddenpropertyid, item_dict)`
Updates an existing ScienceBase Item's Hidden Property.

* `upload_file_to_item(item_dict, filename)`
Upload a file to an existing ScienceBase item. Add the parameter `scrape_file=False` to bypass ScienceBase 
metadata processing.

* `upload_s3_files(itemid, s3_path, filenames)`
Upload a list of files from an external S3 bucket to an existing Item in ScienceBase.

* `upload_cloud_file_to_item(item_id, filename)`
Upload a file to cloud storage on an existing Item in ScienceBase. NOTE: While the Item JSON is returned by this method, it
does take some time to process files uploaded to cloud storage, so the return JSON may not include the new file.
Additionally, automatic processing of shapefiles, TIFFs, XML metadata etc. does not currently occur on cloud files 
at this time. In order to utilize those features, use `upload_file_to_item()`.

* `upload_files_and_update_item(item_dict, [filename,...])`
Upload a set of files and update an existing ScienceBase item. Add the parameter `scrape_file=False` to bypass
ScienceBase metadata processing.

* `upload_files_and_upsert_item(item_dict, [filename,...])`
Upload multiple files and create or update a ScienceBase item. Add the parameter `scrape_file=False` to bypass
ScienceBase metadata processing.

* `replace_file(filename, item_dict)`
Replace a file on a ScienceBase Item.  This method will replace all files named the same as the new file,
whether they are in the files list or in a facet.

* `upload_file(filename, mimetype)`
(Advanced usage) Upload a file to ScienceBase.  The file will be staged in a temporary area.  In order
to attach it to an Item, the pathOnDisk must be added to an Item files entry, or one of a facet's file entries.

* `add_extent(item_id, feature_geojson)`
Add features to the item footprint from Feature or FeatureCollection geojson.

* `start_spatial_service(item_id, filename)`
Creates a spatial service on a published ScienceBase service definition (.sd) file in ArcGIS Online.

* `stop_spatial_service(item_id, filename)`
Stops a spatial service that had been published on a ScienceBase service definition (.sd) file in ArcGIS Online.

* `publish_array_to_public_bucket(item_id, filenames)`
Publish a list of files on an item to the public S3 publish bucket.

* `unpublish_array_from_public_bucket(item_id, filenames)`
Unpublish a list of files on an item from the public S3 publish bucket.

### Item Permissions
* `get_permissions(item_id)`
Get permission JSON for the item identified by item_id.

* `set_permissions(item_id, acls)`
Set permissions for the item identified by item_id. WARNING: Advanced use only. ACL JSON must be created properly. 
Use one of the ACL helper methods if possible (below).

* `add_acl_user_read(user_name, item_id)`
Add a READ ACL for the given user on the specified item.

* `remove_acl_user_read(user_name, item_id)`
Remove the READ ACL for the given user on the specified item.

* `add_acl_user_write(user_name, item_id)`
Add a WRITE ACL for the given user on the specified item.

* `remove_acl_user_write(user_name, item_id)`
Remove a WRITE ACL for the given user on the specified item.

* `add_acl_role_read(role_name, item_id)`
Add a READ ACL for the given role on the specified item.

* `remove_acl_role_read(role_name, item_id)`
Remove a READ ACL for the given role on the specified item.

* `add_acl_role_write(role_name, item_id)`
Add a WRITE ACL for the given role on the specified item.

* `remove_acl_role_write(role_name, item_id)`
Remove a WRITE ACL for the given role on the specified item.

* `set_acls_inherit(read_write, item_id)`
Set the item to inherit ACLs from its parent item.

* `set_acls_inherit_read(item_id)`
Set the item to inherit READ ACLs from its parent item.

* `set_acls_inherit_write(item_id)`
Set the item to inherit WRITE ACLs from its parent item.

* `publish_item(item_id)`
Publish the item, adding PUBLIC read permisisons. User must be USGS or in the publisher role.

* `unpublish_item(item_id)`
Unpublish the item, removing PUBLIC read permisisons.

* `has_public_read(acls)`
Return whether the given ACLs include public READ permissions.

* `print_acls(acls)`
Pretty print the given ACL JSON.

### Delete
* `delete_item(item_dict)`
Delete an existing ScienceBase item.

* `delete_items(item_ids)`
Delete multiple ScienceBase Items.  This is much more efficient than using delete_item() for multiple deletions, as it
performs the action server-side in one call to ScienceBase.

* `delete_file(sb_filename, item_dict)`
Delete a file on a ScienceBase Item.  This method will delete all files with 
the provided name, whether they are in the files list or on a facet.

* `delete_hidden_property(item_id, hiddenpropertyid)`
Delete an existing Item's specific Hidden Property item.

* `undelete_item(item_id)`
Undelete a ScienceBase item.

### Move
* `move_item(item_id, parent_id)`
Move the ScienceBase Item with the given item_id under the ScienceBase Item with the given parent_id.

* `move_items(item_ids, parent_id)`
Move all of the ScienceBase Items with the given item_ids under the ScienceBase Item with the given parent_id.

### Search
For more in-depth search examples, see the `Searching ScienceBase with sciencebasepy.ipynb` notebook in this repo.

* `find_items_by_any_text(text)`
Find items containing the given text somewhere in the item.

* `find_items_by_title(text)`
Find items containing the given text in the title of the item.

* `find_items(params)`
Find items meeting the criteria in the specified search parameters.  These are the same parameters that you pass
to ScienceBase in an advanced search.

* `find_hidden_property(hidden_property)`
Find ScienceBase Items by hidden property value. hidden_property: ScienceBase Item Hidden Property JSON: 
`{"type": ..., "value": ...}`. Returns Item Hidden Property JSON containing the first page of matching 
ScienceBase Items. Use the next() method for subsequent pages.

* `find_items_by_filter_and_hidden_property(params, hidden_property)`
Find items meeting the criteria in the specified search parameters and hidden property JSON. Hidden property JSON contains
two fields, "type" and "value" both of which are optional. **Warning**: Because of the way hidden property results must be 
joined to ScienceBase Catalog search results, this method returns all matching items. Queries returning too many items may 
be blocked by ScienceBase.

* `next(results)`
Get the next page of results, where *results* is the current search results.

* `previous(results)`
Get the previous page of results, where *results* is the current search results.

### Shortcuts
* `get_shortcut_ids(item_id)`
Get the IDs of all ScienceBase Items shortcutted from a given item.
    
* `create_shortcut(item_id, parent_id)`
Create a shortcut on the ScienceBase Item with the id parent_id to another Item with id item_id.
        
* `remove_shortcut(item_id, parent_id)`
Remove a shortcut from the ScienceBase Item with the id parent_id to another Item with id item_id.

### Relationships (ItemLinks)
* `get_item_link_types()`
Get ItemLink type JSON list from the vocabulary server.

* `get_item_link_type_by_name(link_type_name)`
Get ItemLink type JSON object from the vocabulary server for the given type.

* `get_item_links(item_id)`
Get ItemLink (relationship) JSON describing relationships involving the Item with the given ID.

* `create_item_link(from_item_id, to_item_id, link_type_id, reverse=False)`
Create an ItemLink between the two items of the specified type.

* `create_related_item_link(from_item_id, to_item_id)`
Create a 'related' ItemLink between the two items.

### Helpers
* `get_directory_contact(party_id)`
Get the Directory Contact JSON for the contact with the given party ID.

* `get_sbcontact_from_directory_contact(directory_contact, sbcontact_type)`
Convert the given Directory Contact JSON into valid ScienceBase Item contact JSON.

Example Usage
-------------

````python
    import sciencebasepy
    import os

    sb = sciencebasepy.SbSession()

    # Get a public item.  No need to log in.
    item_json = sb.get_item('505bc673e4b08c986b32bf81')
    print "Public Item: " + str(item_json)

    # Get a private item.  Need to log in first.
    username = raw_input("Username:  ")
    sb.loginc(str(username))
    # Need to wait a bit after the login or errors can occur
    time.sleep(5)
    item_json = sb.get_item(sb.get_my_items_id())
    print "My Items: " + str(item_json)

    # Create a new item.  The minimum required is a title for the new item, and the parent ID
    new_item = {'title': 'This is a new test item',
        'parentId': sb.get_my_items_id(),
        'provenance': {'annotation': 'Python ScienceBase REST test script'}}
    new_item = sb.create_item(new_item)
    print "NEW ITEM: " + str(new_item)

    # Upload a file to the newly created item
    new_item = sb.upload_file_to_item(new_item, 'sciencebasepy.py')
    print "FILE UPDATE: " + str(new_item)

    # List file info from the newly created item
    ret = sb.get_item_file_info(new_item)
    for fileinfo in ret:
        print "File " + fileinfo["name"] + ", " + str(fileinfo["size"]) + "bytes, download URL " + fileinfo["url"]

    # Download zip of files from the newly created item
    ret = sb.get_item_files_zip(new_item)
    print "Downloaded zip file " + str(ret)

    # Download all files attached to the item as individual files, and place them in the
    # tmp directory under the current directory.
    path = "./tmp"
    if not os.path.exists(path):
        os.makedirs(path)
    ret = sb.get_item_files(new_item, path)
    print "Downloaded files " + str(ret)

    # Delete the newly created item
    ret = sb.delete_item(new_item)
    print "DELETE: " + str(ret)

    # Upload multiple files to create a new item
    ret = sb.upload_files_and_create_item(sb.get_my_items_id(), ['sciencebasepy.py','readme.md'])
    print str(ret)

    # Search
    items = sb.find_items_by_any_text(username)
    while items and 'items' in items:
        for item in items['items']:
            print item['title']
        items = sb.next(items)

    # Logout
    sb.logout()
````

# Developer Notes

To publish to pypi, follow the instructions [here](https://packaging.python.org/tutorials/packaging-projects/)
