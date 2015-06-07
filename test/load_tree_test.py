import unittest
from mock import MagicMock

from gi.repository import Gtk

import sys 
import os
dir = os.path.dirname(__file__)
path = os.path.join(dir, '..')
sys.path.append(path)
from main import Application


# Test Class which verify the loading of the treestore with a directory passed in parameter
class LoadTreeTestCase(unittest.TestCase):
    
    # Stolen from Kiwi
    @classmethod
    def refreshGUI(self):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        
    def getIterName(self, iter):
        index= self.app.treestore.get_string_from_iter(iter)
        return self.app.treestore[index][0]

    @classmethod
    def setUpClass(self):
        self.app = Application()
    

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def testInitTree(self):
        self.assertNotEqual(self.app.treestore, None, "TreeStore should not be None")
        self.assertEqual(self.app.treestore.get_iter_first(), None, "TreeStore should be empty")
        
    # load a music directory and check that the tree node matches the expectation 
    def testTree(self):
        
        # mock in order to pass the file path
        mockedFile = MagicMock()
        dir = os.path.dirname(__file__)
        path = os.path.join(dir, 'zik')
        mockedFile.get_path = MagicMock(return_value=path)
        
        fileChoser = self.app.builder.get_object("filechooserbutton1")
        fileChoser.get_file = MagicMock(return_value=mockedFile) 
        
        # trigger the file_set event
        self.app.builder.get_object("filechooserbutton1").emit("file_set")
        
        # refresh the UI
        self.refreshGUI()
        
        
        # check that the treestore have a root node
        iter = self.app.treestore.get_iter_first()
        self.assertNotEqual(self.app.treestore.get_iter_first(), None, "TreeStore should not be empty")
        
        # Check all the nodes
        iterName = self.getIterName(iter)
        self.assertEqual(iterName, "zik", "Root node should be 'zik', Got '"+str(iterName)+"'")
        
        iter = self.app.treestore.iter_children(iter)
        iterName = self.getIterName(iter)
        self.assertEqual(iterName, "Taranta Fusion", "Node should be 'Taranta Fusion', Got '"+str(iterName)+"'")
        
        self.assertEqual(self.app.treestore.iter_next(iter), None, "Unexpected Node")
        
        iter = self.app.treestore.iter_children(iter)
        iterName = self.getIterName(iter)
        self.assertEqual(iterName, "Project", "Node should be 'Project', Got '"+str(iterName)+"'")
        
        self.assertEqual(self.app.treestore.iter_next(iter), None, "Unexpected Node")
        
        iter = self.app.treestore.iter_children(iter)
        iterName = self.getIterName(iter)
        self.assertEqual(iterName, "Fimmene fimmene.mp3", "Node should be 'Fimmene fimmene.mp3', Got '"+str(iterName)+"'")
        
        iter = self.app.treestore.iter_next(iter)
        iterName = self.getIterName(iter)
        self.assertEqual(iterName, "Lu ruscio de lu mare.mp3", "Node should be 'Lu ruscio de lu mare.mp3', Got '"+str(iterName)+"'")
        
        self.assertEqual(self.app.treestore.iter_next(iter), None, "Unexpected Node")

if __name__ == '__main__':
    unittest.main()

