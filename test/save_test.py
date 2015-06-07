import unittest
from mock import MagicMock

from gi.repository import Gtk

import sys 
import os
dir = os.path.dirname(__file__)
path = os.path.join(dir, '..')
sys.path.append(path)
from main import Application

import time


# test the saving of the modification on a track
class  SaveTestCase(unittest.TestCase):
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
        
        
    def testSave(self):
        #get the value of the metadatas after broadcast
        modMetadataStr=self.app.treestore["0:0:0:0"][3]
        modMetadataMap=dict([line.split("|=|") for line in modMetadataStr.split("\n")])
        
        curArtist = modMetadataMap["artist"]
        # change the artist name
        modMetadataMap["artist"] = "modification"
        
        # affect the new metadatas in the store
        self.app.treestore["0:0:0:0"][3] = "\n".join(["|=|".join(item) for item in modMetadataMap.items()])
        
        # trigger the click on the save button
        self.app.builder.get_object("saveButton").emit("clicked")
        # refresh the UI
        self.refreshGUI()
        time.sleep(0.5)
        
        # check that the modified metadata contain the new artist name
        modMetadataStr=self.app.treestore["0:0:0:0"][3]
        modMetadataMap=dict([line.split("|=|") for line in modMetadataStr.split("\n")])
        self.assertEqual(modMetadataMap["artist"], "modification", "The metadata should be modified, Got : "+modMetadataMap["artist"])
        
        # check that the base metadata contain the new artist name
        metadataStr=self.app.treestore["0:0:0:0"][2]
        metadataMap=dict([line.split("|=|") for line in metadataStr.split("\n")])
        self.assertEqual(metadataMap["artist"], "modification", "The metadata should be modified, Got : "+metadataMap["artist"])
        
        
        # revert the modification
        modMetadataMap["artist"] = curArtist
        
        self.app.treestore["0:0:0:0"][3] = "\n".join(["|=|".join(item) for item in modMetadataMap.items()])
        
        # trigger the click on the save button
        self.app.builder.get_object("saveButton").emit("clicked")
        # refresh the UI
        self.refreshGUI()
        time.sleep(0.5)
        
        # check that the modified metadata contain the previous artist name
        modMetadataStr=self.app.treestore["0:0:0:0"][3]
        modMetadataMap=dict([line.split("|=|") for line in modMetadataStr.split("\n")])
        self.assertEqual(modMetadataMap["artist"], curArtist, "The modification should be reverted, Got : "+modMetadataMap["artist"])
        
        # check that the base metadata contain the previous artist name
        metadataStr=self.app.treestore["0:0:0:0"][2]
        metadataMap=dict([line.split("|=|") for line in metadataStr.split("\n")])
        self.assertEqual(metadataMap["artist"], curArtist, "The modification should be reverted, Got : "+metadataMap["artist"])
        
        

if __name__ == '__main__':
    unittest.main()

