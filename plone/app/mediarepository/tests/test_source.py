import unittest2 as unittest
from plone.app.testing import setRoles, TEST_USER_ID
from plone.app.mediarepository.testing import MEDIAREPOSITORY_INTEGRATION_TESTING
import transaction

from plone.uuid.interfaces import IUUID
from plone.app.mediarepository.source import MediaRepoSourceBinder
from plone.formwidget.contenttree.source import UUIDSource

class MediaRepositorySourceTest(unittest.TestCase):
    layer = MEDIAREPOSITORY_INTEGRATION_TESTING
    gif = 'GIF89a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\x003\x00!\xf9\x04\x01\x00\x00\x01\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'
    
    def getLogger(self, value):
        return 'plone.app.mediarepository'
    
    def test_source(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        
        # Make sure the repo has a few test images
        repo = portal['media-repository']
        self.assertEquals(repo.portal_type,'media_repository')
        repo.invokeFactory('Image', 'test-image1', title='Test Image 1', image=self.gif)
        repo.invokeFactory('Image', 'test-image2', title='Test Image 2', image=self.gif)
        portal.invokeFactory('Image', 'maverick-image', title='This image isn\'t in the repo', image=self.gif)
        transaction.commit()
        
        # Bind source to site root, should have a UUIDSource
        source = MediaRepoSourceBinder()(portal)
        self.assertTrue(isinstance(source,UUIDSource))
        self.assertEquals(source.navigation_tree_query['path']['query'],'/plone/media-repository')
        
        # Find a term by token
        term = source.getTermByToken('/plone/media-repository/test-image1')
        self.assertEquals(term.title,'Test Image 1')
        self.assertEquals(term.token,'/plone/media-repository/test-image1')
        self.assertEquals(term.value,IUUID(repo['test-image1']))
        
        #TODO: What about things not in the repository?
