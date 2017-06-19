import unittest
import getpass
from pysb import SbSession
from os import listdir
from os.path import isfile, join
from six.moves import input

class TestPysbMethods(unittest.TestCase):
    SB_CATALOG_ITEM_ID = '4f4e4760e4b07f02db47df9c'
    BETA_TEST_COMMUNITY_ID = '54d518d8e4b0afcce73d1a65'
    TEST_USER = None
    TEST_PASSWORD = None

    @classmethod
    def setUpClass(cls):
        super(TestPysbMethods, cls).setUpClass()

        cls.TEST_USER = input("Username:  ")
        cls.TEST_PASSWORD = getpass.getpass()

    def test_get_item(self):
        sb = SbSession('beta')
        item = sb.get_item(self.SB_CATALOG_ITEM_ID)
        self.assertTrue(item is not None)
        self.assertEqual(item['title'], 'ScienceBase Catalog')

    def test_ancestors_field_in_find_items(self):
        sb = SbSession('beta')
        itemsJson = sb.find_items({'parentId':self.BETA_TEST_COMMUNITY_ID, 'fields':'parentId,ancestors'})
        self.assertTrue(itemsJson['items'] is not None)
        self.assertTrue(isinstance(itemsJson['items'], list))
        self.assertTrue(len(itemsJson['items']) > 0)
        item = itemsJson['items'][0]
        self.assertTrue(isinstance(item['ancestors'], list))
        self.assertTrue(item['parentId'] is not None)
        self.assertTrue(item['parentId'] in item['ancestors'])

    def test_ancestors_field_in_get_item(self):
        sb = SbSession('beta')
        item = sb.get_item(self.BETA_TEST_COMMUNITY_ID, {'fields':'parentId,ancestors'})
        self.assertTrue(isinstance(item['ancestors'], list))
        self.assertTrue(item['parentId'] is not None)
        self.assertTrue(item['parentId'] in item['ancestors'])

    def test_upload_shapefile_no_scrape(self):
        sb = SbSession('beta').login(self.TEST_USER, self.TEST_PASSWORD)
        file_dir = 'test/data/FHP_Great_Lakes_Basin_boundary'
        files = ["%s/%s" % (file_dir, f) for f in listdir(file_dir) if isfile(join(file_dir, f))]

        my_items_id = sb.get_my_items_id()
        # Creating new item from shapefile upload
        item = sb.upload_files_and_upsert_item({'parentId': my_items_id}, files, scrape_file=False)
        # Delete the item before the assertions to make sure it gets deleted
        sb.delete_item(item)
        self.assertIsNotNone(item)
        self.assertIsNotNone(item['files'])
        self.assertFalse('facets' in item)

    def test_upload_shapefile_individual_no_scrape(self):
        sb = SbSession('beta').login(self.TEST_USER, self.TEST_PASSWORD)
        file_dir = 'test/data/FHP_Great_Lakes_Basin_boundary'
        files = ["%s/%s" % (file_dir, f) for f in listdir(file_dir) if isfile(join(file_dir, f))]

        # Updating existing item with shapefile, uploading files individually

        item = sb.create_item({'parentId': sb.get_my_items_id(), 'title':'Pysb Shapefile Upload Test'})
        for f in files:
            item = sb.upload_file_to_item(item, f, scrape_file=False)
        # Delete the item before the assertions to make sure it gets deleted
        sb.delete_item(item)
        self.assertIsNotNone(item)
        self.assertIsNotNone(item['files'])
        self.assertFalse('facets' in item)

if __name__ == '__main__':
    unittest.main()