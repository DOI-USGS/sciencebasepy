import sciencebasepy
import getpass
import os

# Establish a session.
sb = sciencebasepy.SbSession()

# Get a public item.  No need to log in.
item_json = sb.get_item('505bc673e4b08c986b32bf81')
print("Public Item: " + str(item_json))

# Example for working with access-restricted item.  A user will need to log in first.
username = getpass.getuser() + '@usgs.gov'  # (or appropriate username@domain)
sb.loginc(str(username))
print("You are now connected.")

item_json = sb.get_item(sb.get_my_items_id())
print("My Items: " + str(item_json))

# Create a new item.  The minimum required is a title for the new item, and the parent ID
new_item = {'title': 'This is a new test item',
            'parentId': sb.get_my_items_id(),
            'provenance': {'annotation': 'Python ScienceBase REST test script'}}
new_item = sb.create_item(new_item)
print("NEW ITEM: " + str(new_item))

# Upload a file to the newly created item
new_item = sb.upload_file_to_item(new_item, 'sciencebasepy.py')
print("FILE UPDATE: " + str(new_item))

# List file info from the newly created item
ret = sb.get_item_file_info(new_item)
for fileinfo in ret:
    print("File " + fileinfo["name"] + ", " + str(fileinfo["size"]) + "bytes, \
    download URL " + fileinfo["url"])

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
ret = sb.delete_item(new_item)
print("DELETE: " + str(ret))

# Upload multiple files to create a new item
ret = sb.upload_files_and_create_item(sb.get_my_items_id(), ['sciencebasepy.py', 'readme.md'])
print(str(ret))

# Search
items = sb.find_items_by_any_text(username)
while items and 'items' in items:
    for item in items['items']:
        print(item['title'])
    items = sb.next(items)

# Logout
sb.logout()