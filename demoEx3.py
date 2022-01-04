import sciencebasepy
import time


FILE_NAME1 = 'test.txt'
FILE_NAME2 = 'testupload.txt'
ITEM_ID = '619c1c66d34eb622f692fe99'

sb = sciencebasepy.SbSession()


# Get a private item.  Need to log in first.
username = input("Username:  ")
sb.loginc(str(username))
print("logged in")
print("My Items ID:" + str(sb.get_my_items_id()))

time.sleep(5)

# publish array of files to public bucket

sb.publish_array_to_public_bucket(ITEM_ID, [FILE_NAME1, FILE_NAME2])