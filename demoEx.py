#############################################################################################################################
#
#           Demo File to test new features in sb3  (SbSessionEx)
#           Make changes to the following lines
#
#           Line 21 : Full file path of the file you want to upload
#           Line 22 : File name after it has been uploaded to sbgraphql, this is the filename that will appear in sbgraphql
#           Line 23 : Item Id is sciencebase, that you want to upload to
#           Lines 28 - 29: Uncomment line 28 to run the script in production, Uncomment line 29 to run the script in "beta"
#           Line 34 : Comment this line if you want don't want use your login email and type your email
#           Line 36 : Uncomment this line and comment the line about if you want to enter you email using the script
#
#############################################################################################################################

import logging

from sb3 import SbSessionEx
from pprint import pprint
import time

FILE_PATH = '/Users/hshakya/Downloads/ORI_n6630w15515P_1.tif'
FILE_NAME = 'ORI_n6630w15515P_2ABCD.tif'
ITEM_ID = '601abc90d34e5bff6edfa4e1'

#
# Main
#
# sb = SbSessionEx.SbSessionEx()
sb = SbSessionEx.SbSessionEx('beta')
# sb.setLoggingEx(level=logging.INFO)


# Get a private item.  Need to log in first.
username =  'hshakya@contractor.usgs.gov'
# username =  input("Username:  ")
sb.logincEx(str(username))

# Upload a File using GraphQL
sb.upload_large_file_upload_session(ITEM_ID, FILE_NAME, FILE_PATH)
