import sciencebasepy

FILE_PATH = 'C:/Apogee Engineering/testupload.txt'
FILE_NAME = 'testupload.txt'
ITEM_ID = '61534834d34e0df5fb9c5c91'

sb = sciencebasepy.SbSession()


# Get a private item.  Need to log in first.
print("going to log in")
username = "k.rajakr98@gmail.com"
password = "usgsTest123!"
sb.login(username, password)
print("logged in")
print("My Items ID:" + str(sb.get_my_items_id()))

# Upload a File using GraphQL
#print(sb.upload_large_file(ITEM_ID, FILE_PATH, FILE_NAME))
