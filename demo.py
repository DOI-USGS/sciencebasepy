from __future__ import print_function

import os
import sciencebasepy

#
# Main
#
PERMANENT_ITEM_ID = '505bc673e4b08c986b32bf81'
DELETE_TEST_ITEMS = True
sb = sciencebasepy.SbSession()

# Get a public item.  No need to log in.
item_json = sb.get_item(PERMANENT_ITEM_ID)
print("Public Item: " + str(item_json))

# Get a private item.  Need to log in first.
username = input("Username:  ")
sb.loginc(str(username))


item_json = sb.get_item(sb.get_my_items_id())
print("My Items: " + str(item_json))

# Create a new item.  The minimum required is a title for the new item, and the parent ID
new_item = {'title': 'This is a new test item',
    'parentId': sb.get_my_items_id(),
    'provenance': {'annotation': 'Python ScienceBase REST test script'}}
new_item = sb.create_item(new_item)
print("NEW ITEM: " + str(new_item))


# Upload a file to the newly created item to local storage
new_item = sb.upload_file_to_item(new_item, 'demo.py')
print("FILE UPDATE: " + str(new_item))

# Upload a file to the newly created item to cloud storage
print(sb.upload_cloud_file_to_item(new_item['id'], 'demo.py'))

# List file info from the newly created item
ret = sb.get_item_file_info(new_item)
for fileinfo in ret:
    print("File " + fileinfo["name"] + ", " + str(fileinfo["size"]) + "bytes, download URL " + fileinfo["url"])

# Download zip of files from the newly created item
ret = sb.get_item_files_zip(new_item)
print("Downloaded zip file " + str(ret))

# Download all files attached to the item as individual files, and place them in the
# tmp directory under the current directory.
path = "./tmp"
if not os.path.exists(path):
    os.makedirs(path)
ret = sb.get_item_files(new_item, path)
print("Downloaded files " + str(ret))

# Delete the newly created item
if DELETE_TEST_ITEMS:
    ret = sb.delete_item(new_item)
    print("DELETE: " + str(ret))

# Upload multiple files to create a new item
new_item = sb.upload_files_and_create_item(sb.get_my_items_id(), ['demo.py','readme.md'])
print(str(new_item))

# Create a new hidden property
new_hidden_property = {'type': 'Note',
    'value': 'test hidden note create'}
new_hidden_property = sb.create_hidden_property(new_item['id'], new_hidden_property)
print("NEW HIDDEN PROPERTY: " + str(new_hidden_property))

# Get all hiddenproperties from an item.
item_json = sb.get_hidden_properties(new_item['id'])
print("Hidden Properties: " + str(new_item))# Get a specific hiddenproperty from an item.
item_json = sb.get_hidden_property(new_item['id'], str(new_hidden_property.get("id", None)))
print("Hidden Property: " + str(item_json))

# Update a new hidden property
updated_hidden_property = {'type': 'Note2',
    'value': 'test hidden note2'}
updated_hidden_property = sb.update_hidden_property(new_item['id'], str(new_hidden_property.get("id", None)), updated_hidden_property)
print("UPDATED HIDDEN PROPERTY: " + str(updated_hidden_property))

# Delete the newly created hidden properties
ret = sb.delete_hidden_property(new_item['id'], str(new_hidden_property.get("id", None)))
print("DELETE: " + str(ret))

# Delete the newly created item
if DELETE_TEST_ITEMS:
    ret = sb.delete_item(new_item)
    print("DELETE: " + str(ret))

# Text search. Only displays the first few pages of results.
max_pages = 3
items = sb.find_items_by_any_text(username)
while items and 'items' in items and max_pages > 0:
    for item in items['items']:
        print(item['title'])
    items = sb.next(items)
    max_pages -= 1

# Logout
sb.logout()
