import unittest
from mock import MagicMock

from gi.repository import Gtk

import sys 
import os
dir = os.path.dirname(__file__)
path = os.path.join(dir, '..')
sys.path.append(path)
from main import Application


# Test Case of the cancel modifications functionnality
class  CancelModifsTestCase(unittest.TestCase):
    
    # Stolen from Kiwi
    @classmethod
    def refreshGUI(self):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
            
    # Apply some modifications on a track file
    def modifyMetadatas(self):
        
        modMetadataStr=self.app.treestore["0:0:0:0"][3]
        modMetadataMap=dict([line.split("|=|") for line in modMetadataStr.split("\n")])
        
        
        modMetadataMap["album"] = "modified"
        modMetadataMap["artist"] = "modified"
        modMetadataMap["copyright"] = "modified"
        modMetadataMap["encodedby"] = "modified"
        modMetadataMap["genre"] = "modified"
        modMetadataMap["organization"] = "modified"
        modMetadataMap["title"] = "modified"
        modMetadataMap["tracknumber"] = "modified"
        modMetadataMap["website"] = "modified"
                        
        self.app.treestore["0:0:0:0"][3] = "\n".join(["|=|".join(item) for item in modMetadataMap.items()])
            
    @classmethod
    def setUpClass(self):
        self.app = Application()
        
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

    def testCancelModifs(self):
        
        # get the initial value of the metadatas
        baseMetadataStr=self.app.treestore["0:0:0:0"][3]
        baseMetadataMap=dict([line.split("|=|") for line in baseMetadataStr.split("\n")])
        
        # apply the modifications
        self.modifyMetadatas()
        
        # get the new value of the metadatas
        modifiedMetadataStr=self.app.treestore["0:0:0:0"][3]
        modifiedMetadataMap=dict([line.split("|=|") for line in modifiedMetadataStr.split("\n")])
        
        # assert that the new metadatas have been changed
        for key,value in modifiedMetadataMap.items():
            self.assertNotEqual(baseMetadataMap[key], modifiedMetadataMap[key], "The metadatas should be different : Base "+baseMetadataMap[key] + ", Modified : "+modifiedMetadataMap[key])
            
        # trigger a click on the cancel button
        self.app.builder.get_object("cancelButton").emit("clicked")
        
        # refresh the UI
        self.refreshGUI()
        
        #get the value of the metadatas after cancel
        canceledMetadataStr=self.app.treestore["0:0:0:0"][3]
        canceledMetadataMap=dict([line.split("|=|") for line in canceledMetadataStr.split("\n")])
        
        # assert that the canceled metadatas are the same than the base 
        for key,value in canceledMetadataMap.items():
            self.assertEqual(baseMetadataMap[key], canceledMetadataMap[key], "The metadatas should be equal : Base "+baseMetadataMap[key] + ", Modified : "+canceledMetadataMap[key])
        
        

if __name__ == '__main__':
    unittest.main()

