import unittest
from pysb import SbSession

class TestPysbMethods(unittest.TestCase):
    SB_CATALOG_ITEM_ID = '4f4e4760e4b07f02db47df9c'

    def test_get_item(self):
        sb = SbSession()
        item = sb.get_item(self.SB_CATALOG_ITEM_ID)
        self.assertTrue(item is not None)
        self.assertEqual(item['title'], 'ScienceBase Catalog')

if __name__ == '__main__':
    unittest.main()