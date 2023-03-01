from sciencebasepy import SbSession

FILE_NAME = 'tests/resources/Python.jpg'

sb = SbSession()
CREATE_ITEM = True

# Login to ScienceBase
username = input("Username:  ")
sb.loginc(str(username))
#sb.debug() # Uncomment this line for verbose output

if CREATE_ITEM:
    # Create test item
    new_item = {'title': 'Cloud Upload Test',
        'parentId': sb.get_my_items_id(),
        'provenance': {'annotation': 'Python ScienceBase REST test script'}}
    new_item = sb.create_item(new_item)
    item_id = new_item['id']

else:
    # Set this to a known writeable item ID and CREATE_ITEM to False for testing
    # without creating a new item
    item_id = "some_item_id"

# Upload a File using GraphQL to the test item
print(sb.upload_cloud_file_to_item(item_id, FILE_NAME))
