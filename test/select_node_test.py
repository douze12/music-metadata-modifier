import unittest
from mock import MagicMock

import pygtk
pygtk.require("2.0")
from gi.repository import Gtk

import sys 
import os
sys.path.append(os.path.abspath(".."))
from main import Application


# Test Class that verify the selection of a node in the directory
# and the 
class  SelectNodeTestCase(unittest.TestCase):
   # Stolen from Kiwi
    @classmethod 
    def refreshGUI(self):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
    
    
    # check the children elements in the metadata grid and verify the values of each child
    def checkGrid(self, expectedValues):
        
        # get the grid where the common metadatas are displayed
        grid=self.app.builder.get_object("metadata_grid")
        
        i = 1
        for tuple in expectedValues:
            child = self.app.builder.get_object("metadata_grid").get_child_at(1 , i)
            # check child class
            self.assertTrue(isinstance(child, Gtk.Label), "Bad Child Type")
            # check the label value
            self.assertEqual(child.get_label(), tuple[0], "Expected label "+tuple[0]+", Got : "+child.get_label())
            
            child = self.app.builder.get_object("metadata_grid").get_child_at(2, i)
            # check child class
            self.assertTrue(isinstance(child, Gtk.Label), "Bad Child Type")
            # check the label value
            self.assertEqual(child.get_label(), tuple[1], "Expected label "+tuple[1]+", Got : "+child.get_label())
            
            child = self.app.builder.get_object("metadata_grid").get_child_at(3, i)
            # check child class
            self.assertTrue(isinstance(child, Gtk.Entry), "Bad Child Type")
            # check the label value
            self.assertEqual(child.get_text(), tuple[2], "Expected entry value "+tuple[2]+", Got : "+child.get_text())
            
            i+=1

    @classmethod 
    def setUpClass(self):  
        self.app = Application()
        
        # mock in order to pass the file path
        mockedFile = MagicMock()
        mockedFile.get_path = MagicMock(return_value=os.path.abspath("zik")) 
        
        fileChoser = self.app.builder.get_object("filechooserbutton1")
        fileChoser.get_file = MagicMock(return_value=mockedFile) 
        
        # trigger the file_set event
        self.app.builder.get_object("filechooserbutton1").emit("file_set")
        
        # refresh the UI
        self.refreshGUI()
        
        
    # selection of the root directory 
    def testSelectRootDirectory(self):
        
        # mock in order to pass the root node as cursor
        self.app.builder.get_object("foundFileTree").get_cursor = MagicMock(return_value=("0", None))  
        
        # trigger the file_set event
        self.app.builder.get_object("foundFileTree").emit("cursor_changed")
        
        # refresh the UI
        self.refreshGUI()
        
        
        expectedValues = [
                        ("album", "Project", "Project"),
                        ("artist", "Taranta Fusion", "Taranta Fusion"),
                        ("copyright", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/"),
                        ("encodedby", "Jamendo : http://www.jamendo.com | LAME", "Jamendo : http://www.jamendo.com | LAME"),
                        ("genre", "Unknown", "Unknown"),
                        ("organization", "Jamendo", "Jamendo"),
                        ("title", "", ""),
                        ("tracknumber", "", ""),
                        ("website", "http://www.jamendo.com/en/artist/Taranta_Fusion", "http://www.jamendo.com/en/artist/Taranta_Fusion")
                        ]
        
        self.checkGrid(expectedValues)
        
        
    
    # selection of the artist name directory 
    def testSelectArtistDirectory(self):
        
        # mock in order to pass the root node as cursor
        self.app.builder.get_object("foundFileTree").get_cursor = MagicMock(return_value=("0:0", None))  
        
        # trigger the file_set event
        self.app.builder.get_object("foundFileTree").emit("cursor_changed")
        
        # refresh the UI
        self.refreshGUI()
        
        
        expectedValues = [
                        ("album", "Project", "Project"),
                        ("artist", "Taranta Fusion", "Taranta Fusion"),
                        ("copyright", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/"),
                        ("encodedby", "Jamendo : http://www.jamendo.com | LAME", "Jamendo : http://www.jamendo.com | LAME"),
                        ("genre", "Unknown", "Unknown"),
                        ("organization", "Jamendo", "Jamendo"),
                        ("title", "", ""),
                        ("tracknumber", "", ""),
                        ("website", "http://www.jamendo.com/en/artist/Taranta_Fusion", "http://www.jamendo.com/en/artist/Taranta_Fusion")
                        ]
        
        self.checkGrid(expectedValues)
        
        
    # selection of the album name directory 
    def testSelectAlbumDirectory(self):
        
        # mock in order to pass the root node as cursor
        self.app.builder.get_object("foundFileTree").get_cursor = MagicMock(return_value=("0:0:0", None))  
        
        # trigger the file_set event
        self.app.builder.get_object("foundFileTree").emit("cursor_changed")
        
        # refresh the UI
        self.refreshGUI()
        
        
        expectedValues = [
                        ("album", "Project", "Project"),
                        ("artist", "Taranta Fusion", "Taranta Fusion"),
                        ("copyright", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/"),
                        ("encodedby", "Jamendo : http://www.jamendo.com | LAME", "Jamendo : http://www.jamendo.com | LAME"),
                        ("genre", "Unknown", "Unknown"),
                        ("organization", "Jamendo", "Jamendo"),
                        ("title", "", ""),
                        ("tracknumber", "", ""),
                        ("website", "http://www.jamendo.com/en/artist/Taranta_Fusion", "http://www.jamendo.com/en/artist/Taranta_Fusion")
                        ]
        
        self.checkGrid(expectedValues)
        
        
    # selection of the first track
    def testSelectTrackOne(self):
        
        # mock in order to pass the root node as cursor
        self.app.builder.get_object("foundFileTree").get_cursor = MagicMock(return_value=("0:0:0:0", None))  
        
        # trigger the file_set event
        self.app.builder.get_object("foundFileTree").emit("cursor_changed")
        
        # refresh the UI
        self.refreshGUI()
        
        
        expectedValues = [
                        ("album", "Project", "Project"),
                        ("artist", "Taranta Fusion", "Taranta Fusion"),
                        ("copyright", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/"),
                        ("encodedby", "Jamendo : http://www.jamendo.com | LAME", "Jamendo : http://www.jamendo.com | LAME"),
                        ("genre", "Unknown", "Unknown"),
                        ("organization", "Jamendo", "Jamendo"),
                        ("title", "Fimmene fimmene", "Fimmene fimmene"),
                        ("tracknumber", "02", "02"),
                        ("website", "http://www.jamendo.com/en/artist/Taranta_Fusion", "http://www.jamendo.com/en/artist/Taranta_Fusion")
                        ]
        
        self.checkGrid(expectedValues)
        
        
    # selection of the second track
    def testSelectTrackTwo(self):
        
        # mock in order to pass the root node as cursor
        self.app.builder.get_object("foundFileTree").get_cursor = MagicMock(return_value=("0:0:0:1", None))  
        
        # trigger the file_set event
        self.app.builder.get_object("foundFileTree").emit("cursor_changed")
        
        # refresh the UI
        self.refreshGUI()
        
        
        expectedValues = [
                        ("album", "Project", "Project"),
                        ("artist", "Taranta Fusion", "Taranta Fusion"),
                        ("copyright", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/", "2011-10-30T01:59:54+01:00 Taranta Fusion. Licensed to the public under http://creativecommons.org/licenses/by-sa/3.0/ verify at http://www.jamendo.com/album/101114/"),
                        ("encodedby", "Jamendo : http://www.jamendo.com | LAME", "Jamendo : http://www.jamendo.com | LAME"),
                        ("genre", "Unknown", "Unknown"),
                        ("organization", "Jamendo", "Jamendo"),
                        ("title", "Lu ruscio de lu mare", "Lu ruscio de lu mare"),
                        ("tracknumber", "01", "01"),
                        ("website", "http://www.jamendo.com/en/artist/Taranta_Fusion", "http://www.jamendo.com/en/artist/Taranta_Fusion")
                        ]
        
        self.checkGrid(expectedValues)
        
if __name__ == '__main__':
    unittest.main()

