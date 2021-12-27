import sciencebasepy
import time

FILE_PATH = 'C:/Apogee Engineering/testupload.txt'
FILE_NAME = 'testupload.txt'
ITEM_ID = '619c1c66d34eb622f692fe99'

sb = sciencebasepy.SbSession()


# Get a private item.  Need to log in first.
print("going to log in")
username = input("Username:  ")
sb.loginc(str(username))
print("logged in")
print("My Items ID:" + str(sb.get_my_items_id()))

time.sleep(5)

# Upload a File using GraphQL
print(sb.upload_large_file(ITEM_ID, FILE_PATH, FILE_NAME))
