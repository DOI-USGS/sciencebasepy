from sciencebasepy import SbSession

FILE_NAME = 'tests/resources/sample_error.png'

sb = SbSession()

# Login to ScienceBase
username = input("Username:  ")
sb.loginc(str(username))

# Create test item
new_item = {'title': 'Cloud Upload Test',
    'parentId': sb.get_my_items_id(),
    'provenance': {'annotation': 'Python ScienceBase REST test script'}}
new_item = sb.create_item(new_item)

# Upload a File using GraphQL to the test item
print(sb.upload_cloud_file_to_item(new_item['id'], FILE_NAME))
