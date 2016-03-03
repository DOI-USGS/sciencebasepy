import os
from pysb import pysb

#
# Main
#
if __name__ == "__main__":
    sb = pysb.SbSession()

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
    newItem = sb.uploadFileToItem(newItem, 'demo-legacy.py')
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
    ret = sb.uploadFilesAndCreateItem(sb.getMyItemsId(), ['demo-legacy.py','readme.md'])
    print str(ret)

    # Search
    items = sb.findSbItemsByAnytext(username)
    while items and 'items' in items:
        for item in items['items']:
            print item['title']
        items = sb.next(items)

    # Logout
    sb.logout()
