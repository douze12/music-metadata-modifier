import unittest
from mock import MagicMock

from gi.repository import Gtk

import sys 
import os
dir = os.path.dirname(__file__)
path = os.path.join(dir, '..')
sys.path.append(path)
from main import Application

# test of the broadcast functionnality which broadcast the modification 
# made on a directory node to all the sub tracks
class  BroadcastTestCase(unittest.TestCase):

    # Stolen from Kiwi
    @classmethod
    def refreshGUI(self):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
            
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
    

    def testBroadcast(self):

        # select the root directory in order to have the broadcast button available
        self.app.builder.get_object("foundFileTree").get_cursor = MagicMock(return_value=("0", None))  
        # trigger the file_set event
        self.app.builder.get_object("foundFileTree").emit("cursor_changed")
        # refresh the UI
        self.refreshGUI()
        
        
        # change the value of the input of the artist 
        self.app.builder.get_object("metadata_grid").get_child_at(3 , 2).set_text("Broadcast")
        
        # trigger the click on the broadcast button
        self.app.broadcastButton.emit("clicked")
        
        #get the value of the metadatas after broadcast
        modMetadataStr=self.app.treestore["0:0:0:0"][3]
        modMetadataMap=dict([line.split("|=|") for line in modMetadataStr.split("\n")])
        self.assertEqual(modMetadataMap["artist"], "Broadcast", "The broadcast failed")
        
        modMetadataStr=self.app.treestore["0:0:0:1"][3]
        modMetadataMap=dict([line.split("|=|") for line in modMetadataStr.split("\n")])
        self.assertEqual(modMetadataMap["artist"], "Broadcast", "The broadcast failed")
        

if __name__ == '__main__':
    unittest.main()

