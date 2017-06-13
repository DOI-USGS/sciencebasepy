import unittest
from pysb import SbSession

class TestPysbMethods(unittest.TestCase):
    SB_CATALOG_ITEM_ID = '4f4e4760e4b07f02db47df9c'
    BETA_TEST_COMMUNITY_ID = '54d518d8e4b0afcce73d1a65'

    def test_get_item(self):
        sb = SbSession()
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

if __name__ == '__main__':
    unittest.main()