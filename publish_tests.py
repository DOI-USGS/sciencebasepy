import unittest
import getpass
import json

from pysb import SbSession

class TestPysbMethods(unittest.TestCase):
    USGS_TEST_USER = None
    USGS_TEST_PASSWORD = None
    MYUSGS_TEST_USER = None
    MYUSGS_TEST_PASSWORD = None
    BETA_TEST_COMMUNITY = '56006756e4b025da209d3f2a'

    @classmethod
    def setUpClass(self):
        super(TestPysbMethods, self).setUpClass()

        self.USGS_TEST_USER = 'jllong@usgs.gov'#input("USGS Username:  ")
        self.USGS_TEST_PASSWORD = #getpass.getpass()
        self.MYUSGS_TEST_USER = 'codlong@yahoo.com'#input("MyUSGS Username:  ")
        self.MYUSGS_TEST_PASSWORD = #getpass.getpass()

    def test_usgs_my_items(self):
        sb = SbSession('beta').login(self.USGS_TEST_USER, self.USGS_TEST_PASSWORD)
        item = sb.create_item({'parentId': sb.get_my_items_id(), 'title': 'ACL Test'})
        permissions = sb.get_permissions(item['id'])
        self.assertFalse('PUBLIC' in permissions['read']['acl'])

        permissions['read']['acl'] = ['PUBLIC']
        permissions['read']['inherited'] = False
        permissions = sb.set_permissions(item['id'], permissions)
        self.assertFalse('acl' in permissions['read'] and 'PUBLIC' in permissions['read']['acl'])
        sb.delete_items([item['id']])

    def test_myusgs_public_community(self):
        sb = SbSession('beta').login(self.MYUSGS_TEST_USER, self.MYUSGS_TEST_PASSWORD)
        item = sb.create_item({'parentId': self.BETA_TEST_COMMUNITY, 'title': 'ACL Test'})
        permissions = sb.get_permissions(item['id'])
        self.assertFalse('acl' in permissions['read'] and 'PUBLIC' in permissions['read']['acl'])

        permissions['read']['acl'] = ['PUBLIC']
        permissions['read']['inherited'] = False
        permissions = sb.set_permissions(item['id'], permissions)
        print(item['id'])
        self.assertFalse('acl' in permissions['read'] and 'PUBLIC' in permissions['read']['acl'])
        sb.delete_items([item['id']])

    def test_usgs_public_community(self):        
        sb = SbSession('beta').login(self.USGS_TEST_USER, self.USGS_TEST_PASSWORD)
        item = sb.create_item({'parentId': self.BETA_TEST_COMMUNITY, 'title': 'ACL Test'})
        permissions = sb.get_permissions(item['id'])

        permissions['read']['acl'] = ['PUBLIC']
        permissions['read']['inherited'] = False
        permissions = sb.set_permissions(item['id'], permissions)
        self.assertTrue('acl' in permissions['read'] and 'PUBLIC' in permissions['read']['acl'])
        sb.delete_items([item['id']])

if __name__ == '__main__':
    unittest.main()