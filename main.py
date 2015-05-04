#!/usr/bin/python3
# -*-coding:UTF-8 -*
# TODO
# Needed modules : python-mutagen python-glade2
# Application to manage the metadatas information on music track files
# @author douze12
# @date 26/04/2015

import time
import thread

import pygtk
pygtk.require("2.0")
from gi.repository import Gtk,Pango

from os import listdir
from os.path import isfile, join, isdir

import mutagen


## CONSTANTS
FILE_NAME_INDEX = 0
FILE_PATH_INDEX = 1
METADATA_INDEX = 2
MOD_METADATA_INDEX = 3

# Main class
class Application:
    
    def __init__(self):
        
        # flag used to manually stop the searching thread
        self.stop=False
        
        # load the glade file interface
        self.builder = Gtk.Builder()
        self.builder.add_from_file("window.glade")
        self.builder.connect_signals(self)
        window = self.builder.get_object("window1")
        window.show_all()
        window.connect("delete-event", Gtk.main_quit)
        
        # Hide the progress status grid element
        self.builder.get_object("progressGrid").set_visible(False)
        
        #get the treestore
        self.treestore=self.builder.get_object("foundFileStore")

        # set the rendering class for the file name column
        cell=Gtk.CellRendererText()
        self.builder.get_object("treeColumnFileName").pack_start(cell, True)
        # add markup attribute in order to be able to insert Pango tags in file name
        # necessary for bold
        self.builder.get_object("treeColumnFileName").add_attribute(cell, 'markup', 0)
        
    
    # method called when the user choose a directory with the file selector
    def onChooseFile(self, fileChoser):
        print "Chosen file : "+ fileChoser.get_file().get_path()
        
        # show the progress status grid
        self.builder.get_object("progressGrid").set_visible(True)
        self.builder.get_object("spinner1").start()
        
        # deactivate the file selector during the process
        self.builder.get_object("filechooserbutton1").set_sensitive(False)
        
        self.stop=False
        
        # clear the current tree store
        self.treestore.clear()
        
        # launch the search in a separate thread
        thread.start_new_thread(self.__startSearchThread,(fileChoser.get_file().get_path(),))
        
    
    # method called when the user stop the searching directory process
    def onStopClick(self, source=None, event=None):
        self.stop=True
        
    # method called when the user click on a row in the file tree view
    def onSelectRow(self, source=None, event=None):
        (index,elem)=source.get_cursor()
        
        # get the metadatas of the current row
        metadataStr=self.treestore[index][METADATA_INDEX]
        modMetadataStr=self.treestore[index][MOD_METADATA_INDEX]
        
        
        # if we don't have metadata, we are on a directory
        if (metadataStr == None):
            self.__displayCommonMetadata(index.to_string())
            return
        
        
        metadataMap=self.__transformInMap(metadataStr)
        modMetadataMap=self.__transformInMap(modMetadataStr)
        
        # display the metadata in the information panel
        self.__displayMetadata(index, metadataMap, modMetadataMap, False)
   
    
    # method called when the user change the value of a metadata
    def onChangeMetadata(self, element, userData):
        (elementIndex, key) = userData
        
        #get the edited map metadata
        editedMetadata=self.treestore[elementIndex][MOD_METADATA_INDEX]
        editedMetadataMap=self.__transformInMap(editedMetadata)
        
        # change the value of the metadata with the modified value
        editedMetadataMap[key]=element.get_text()
        
        #reconstitute the new metadata
        self.treestore[elementIndex][MOD_METADATA_INDEX]=self.__transformInString(editedMetadataMap)
        
        # bold the file name if the metadata has changed compared to the originals
        self.__boldModifiedFile(elementIndex)
      
    
    # method called when the user click on the broadcast button
    # the modified metadata will be broadcast to all the tracks 
    # contained in the current directory
    def onBroadcastClick(self, source):
        grid=self.builder.get_object("metadata_grid")
        children=grid.get_children()
        
        # make a map with the metadatas in the entries
        map={}
        for child in children:
            if child.__class__.__name__ == "Entry":
                metadata_name=child.get_name().split("_")[1]
                metadata_value=child.get_text()
                if(len(metadata_value) != 0):
                    map[metadata_name] = metadata_value
        
        
        if(len(map) > 0):
            (index,elem)=self.builder.get_object("foundFileTree").get_cursor()
            iter = self.treestore.iter_children(self.treestore.get_iter(index))
            self.__broadcastModifs(iter, map)
            
    
    # method called when the user click on the save button
    # we save all the modified metadatas to the track files
    def onSaveClick(self,source):
        iter = self.treestore.get_iter_first()
        self.__save(iter)
        # after saving, refresh the metadatas of the current selected element displayed in the panel
        self.__refreshMetadataPanel()
        
    # method called when the user click on the cancel button
    # we cancel all the modifications
    def onCancelClick(self,source):
        iter = self.treestore.get_iter_first()
        self.__cancelModifs(iter)
        # after canceling, refresh the metadatas of the current selected element displayed in the panel
        self.__refreshMetadataPanel()
        
        
    
    
    ###########################################################################
    #######################   PRIVATE METHODS    ##############################
    ###########################################################################
    

    # convert the metadata value in string accoding to the data type
    def __convertInString(self, object):
        oClass=object.__class__.__name__
        
        # if the data type is a list, we just get the first element
        if oClass == "list":
            object=object[0]
            oClass=object.__class__.__name__
        
        # if the data type is allready a string or a unicode string, we return the object with no transformation
        if oClass == "str" or oClass == "unicode":
            return object
        # ASFUnicodeAttribute for .wma music files
        elif oClass == "ASFUnicodeAttribute":
            return object.value
        
        return None

    # scan a folder, extract the music files metadata and fill the tree store 
    # (recursive method)
    def __scanFolder(self,path,treeNode=None):
        
        # list the files in the current direcory
        for file in sorted(listdir(path)):
            
            filePath=join(path,file)
            
            # if the file is a direcory, we recursivly call the scan
            if isdir(filePath):
                print("Directory : "+filePath)
                # add the folder in the tree
                newNode=self.treestore.append(treeNode,[file, filePath,None,None])
                self.__scanFolder(filePath,newNode)
            else:
                print("File : "+filePath)
                
                # check if the file extension is supported
                if(file.endswith(".mp3") or file.endswith(".wma")):
                    metadataMap={}
                    mutaFile = mutagen.File(filePath, easy=True)
                    for key in sorted(mutaFile.keys()):
                        value=mutaFile[key]
                        valueStr=self.__convertInString(value)
                        if valueStr is not None:
                            metadataMap[key]=valueStr
                            
                    metadataStr=self.__transformInString(metadataMap)
                    newNode=self.treestore.append(treeNode,[file,filePath,metadataStr,metadataStr])
                
            
            # the user has manually stopped the scan so we raise an exception
            if self.stop:
                raise Exception("Stop")
    
    
    # we check if we are on a album or artist directory
    def __checkDirectoryType(self, index):
        is_artist=False
        is_album=False
        
        dir_name = self.treestore[index][FILE_NAME_INDEX]
        
        # Check if te current folder is an album or an artist
        # It will be consider as an album if there are some tracks in the directory
        # It will be consider as an arist if there are some directories which contains tracks
        treeiter = self.treestore.iter_children(self.treestore.get_iter(index))
        while treeiter != None:
            iter_index = self.treestore.get_string_from_iter(treeiter)
            metadata = self.treestore[iter_index][METADATA_INDEX]
            
            # the directory is an album if one children has metatdats ( = it's a track)
            is_album |= (metadata != None)
            
            if(metadata == None):
                # no metadat so we are on an other direcory,
                # we have to check the children of that directory
                sub_treeiter = self.treestore.iter_children(treeiter)
                while sub_treeiter != None:
                    iter_index=self.treestore.get_string_from_iter(sub_treeiter)
                    metadata = self.treestore[iter_index][3]
                    
                    # the directory is an artist if a subdirectory contains track files
                    is_artist |= (metadata != None)
                    
                    sub_treeiter=self.treestore.iter_next(sub_treeiter)
            
            # go to the next iterator element
            treeiter=self.treestore.iter_next(treeiter)
        
        print ("Album? %s" % is_album)
        print ("Artist? %s" % is_artist)
        
        return (is_album, is_artist)
    
    
    # transform the metadata string formatted like "key1=value1\nkey2=value2..." 
    # in the corresponding map
    def __transformInMap(self,stringMetatdata):
        return dict([line.split("|=|") for line in stringMetatdata.split("\n")])
    
    
    # transform the metadata map in string formatted like "key1=value1\nkey2=value2..."
    def __transformInString(self,mapMetatdata):
        return "\n".join(["|=|".join(item) for item in mapMetatdata.items()])
    
    
    # bold the parent nodes if there are at least one modified child 
    def __boldParents(self, index):
        
        iter = self.treestore.get_iter(index)
        iter = self.treestore.iter_parent(iter)
        
        while(iter != None):
            index=self.treestore.get_string_from_iter(iter)
            
            if (self.__checkChildrenModified(iter)):
                self.__bold(index)
            else:
                self.__unbold(index)
        
            # get the next parent
            iter=self.treestore.iter_parent(iter)
            
    
    
    # Method which check if an element's metadatas have been modified
    # and set the element name in bold if they have
    def __boldModifiedFile(self, elementIndex):
        
        # check if there is a modification on the metadatas
        if (self.__checkMetadataModified(elementIndex)):
           self.__bold(elementIndex)
        else:
            self.__unbold(elementIndex)
            
        # bold or unbold the parent nodes
        self.__boldParents(elementIndex)
    
    # add bold tag around the file name of the passed index
    def __bold(self, elementIndex):
        file_name=self.treestore[elementIndex][FILE_NAME_INDEX]
        #check if we have allready the <b> tag on the file name
        if(file_name.find("<b>") == -1):
            self.treestore[elementIndex][FILE_NAME_INDEX]="<b>"+file_name+"</b>"
    
    # remove bold tag around the file name of the passed index
    def __unbold(self, elementIndex):
        file_name=self.treestore[elementIndex][FILE_NAME_INDEX]
        # the metadatas are the same than the acual, we remove the <b> tag
        if(file_name.find("<b>") != -1):
            file_name=file_name[file_name.find("<b>")+len("<b>"):file_name.find("</b>")]
            self.treestore[elementIndex][FILE_NAME_INDEX] = file_name
                
        
    # check if at least one child of the passed node has been modified
    def __checkChildrenModified(self, iter):
        
        #get the string index of the iterator
        index=self.treestore.get_string_from_iter(iter)
        
        #get the metadatas of the current iterator
        metadata = self.treestore[index][METADATA_INDEX]
        
        modified = False
        # if we have metadatas => we are on a track
        if (metadata != None):
            modified = self.__checkMetadataModified(index)
        # if the iter element have some children, we check them
        elif (self.treestore.iter_has_child(iter)):
            childIter=self.treestore.iter_children(iter)
            modified = self.__checkChildrenModified(childIter)
        
        # if the current node or one of his child has been modified, we can return True 
        # without check the next siblings
        if (modified):
            return True
            
        # next iterator element
        iter=self.treestore.iter_next(iter)
        if(iter != None):
            return self.__checkChildrenModified(iter)
        
        return False
        
        
    # method which check if the metadata have been modified
    def __checkMetadataModified(self, elementIndex):
        metadata=self.treestore[elementIndex][METADATA_INDEX]
        metadataMap=self.__transformInMap(metadata)
        
        editedMetadata=self.treestore[elementIndex][MOD_METADATA_INDEX]
        editedMetadataMap=self.__transformInMap(editedMetadata)
        
        return metadataMap != editedMetadataMap
    
      
    # get the metadatas in common on all the tracks of a direcory
    def __getCommonMetadatas(self, iter, commonMap):
        
        #get the string index of the iterator
        index=self.treestore.get_string_from_iter(iter)
        
        #get the metadatas of the current iterator
        metadata = self.treestore[index][METADATA_INDEX]
        
        # if we have metadatas => we are on a track
        if (metadata != None):
            metadataMap=self.__transformInMap(metadata)
            
            first = (len(commonMap) == 0)
            
            for key,value in metadataMap.iteritems():
                
                # if we don't have this kind of metadata in the common map, we don't go further
                # except if we are in the first metadata found
                if (first == False and key not in commonMap):
                    continue
                
                # if the metadata is not in the common list, we add it
                if(commonMap.get(key) == None):
                    commonMap[key] = value
                # if the metadata is in the list and the value does not match with the common
                # we flag the metadata to False in order to indicate it's not common 
                elif(commonMap.get(key) != False and commonMap.get(key) != value):
                    commonMap[key] = False
            
            
            # check if the current track contains all the kind of common metadatas
            # => we want only the metadata that exists on all the tracks
            toDel=[]
            for commonKey in commonMap:
                if commonKey not in metadataMap:
                    toDel.append(commonKey)
            for e in toDel:
                del(commonMap[e])
            
        # if the iter element have some children, we check them
        if(self.treestore.iter_has_child(iter)):
            childIter=self.treestore.iter_children(iter)
            self.__getCommonMetadatas(childIter, commonMap)
        
        # next iterator element
        iter=self.treestore.iter_next(iter)
        if(iter != None):
            self.__getCommonMetadatas(iter, commonMap)
    
            
    # when the user select a directory, get the metadatas in common with all
    # the tracks and display a form with them
    def __displayCommonMetadata(self, index):
        map={}
        
        # iterator on the first child
        treeiter = self.treestore.iter_children(self.treestore.get_iter(index))
        
        # get the metadatas in common with all the tracks
        self.__getCommonMetadatas(treeiter, map)
        
        # display the datas in the panel 
        self.__displayMetadata(index, map, map, True)
        
        grid=self.builder.get_object("metadata_grid")
        
        # if  we have none metadata in common, we don't display the broadcast button
        if (len(map) > 0):
            broadcastButton=Gtk.Button("Broadcast",visible=True)
            broadcastButton.connect("clicked",self.onBroadcastClick)
            grid.attach(broadcastButton,1,len(map) + 1,1,1)

        autoTitleButton=Gtk.Button("Magic Wand",visible=True)
        grid.attach(autoTitleButton,2,len(map) + 1,1,1)
        
        
    # broadcast the modified metadatas to all the files from the selected folder
    def __broadcastModifs(self, iter, map):
        
        #get the string index of the iterator
        index=self.treestore.get_string_from_iter(iter)
        
        #get the metadatas of the current iterator
        metadata = self.treestore[index][MOD_METADATA_INDEX]
        
        # if we have metadatas => we are on a track
        if (metadata != None):
            currentMetadata=self.__transformInMap(metadata)
            
            for key,value in currentMetadata.iteritems():
              if key in map:
                  currentMetadata[key]=map[key]
            
            self.treestore[index][MOD_METADATA_INDEX] = self.__transformInString(currentMetadata)
            self.__boldModifiedFile(index)
            
            
        # if the iter element have some children, we check them
        if(self.treestore.iter_has_child(iter)):
            childIter=self.treestore.iter_children(iter)
            self.__broadcastModifs(childIter, map)
        
        # next iterator element
        iter=self.treestore.iter_next(iter)
        if(iter != None):
            self.__broadcastModifs(iter, map)
        
    # change the value of the metatdat and replace it with the new value
    def __changeValue(self,mutaFile, key, newValue):
        
        oldValue = mutaFile[key]
        
        oClass=oldValue.__class__.__name__
        
        # if the metadata is a list, we just take the first element
        if oClass == "list":
            oldValue=oldValue[0]
            oClass=object.__class__.__name__
        
        # check the data type and affect the new value
        if oClass == "str":
            mutaFile[key] = newValue
        elif oClass == "unicode":
            mutaFile[key] = unicode(newValue)
        elif oClass == "ASFUnicodeAttribute":
            oldValue.value = newValue
        
        
    # save the modified metadatas to the track files
    # (recursive method)
    def __save(self,iter):
        #get the string index of the iterator
        index=self.treestore.get_string_from_iter(iter)
        
        #get the metadatas of the current iterator
        metadataStr = self.treestore[index][METADATA_INDEX]
        
        # check if we have metadatas and if they have been modifed
        if (metadataStr != None and self.__checkMetadataModified(index)):
            
            modMetadataStr = self.treestore[index][MOD_METADATA_INDEX]
            mapModMetadata=self.__transformInMap(modMetadataStr)
            
            filePath = self.treestore[index][FILE_PATH_INDEX]
            
            mutaFile = mutagen.File(filePath, easy=True)
            
            for key,value in mapModMetadata.iteritems():
                if key in mutaFile.keys():
                    self.__changeValue(mutaFile, key, value)
                    
            print("Save file "+filePath)
            mutaFile.save()
            
            self.treestore[index][METADATA_INDEX] = self.treestore[index][MOD_METADATA_INDEX]
            
            # unbold the file name
            self.__boldModifiedFile(index)
            
        
        # if the iter element have some children, we check them
        if(self.treestore.iter_has_child(iter)):
            childIter=self.treestore.iter_children(iter)
            self.__save(childIter)
        
        # next iterator element
        iter=self.treestore.iter_next(iter)
        if(iter != None):
            self.__save(iter)
            
            
    # cancel all the modifications
    # (recursive method)
    def __cancelModifs(self,iter):
        #get the string index of the iterator
        iter_index=self.treestore.get_string_from_iter(iter)
        
        #get the metadatas of the current iterator
        metadataStr = self.treestore[iter_index][METADATA_INDEX]
        
        # if we have metadatas => we are on a track
        if (metadataStr != None):
            mapMetadata=self.__transformInMap(metadataStr)
            
            # replace the modified metadatas with the original ones
            self.treestore[iter_index][MOD_METADATA_INDEX] = self.__transformInString(mapMetadata)
            self.__boldModifiedFile(iter_index)
            
            
        # if the iter element have some children, we check them
        if(self.treestore.iter_has_child(iter)):
            child_iter=self.treestore.iter_children(iter)
            self.__cancelModifs(child_iter)
        
        # next iterator element
        iter=self.treestore.iter_next(iter)
        if(iter != None):
            self.__cancelModifs(iter)
    
    # refresh the right panel which display the metadata of the selected element
    def __refreshMetadataPanel(self):
        
        #get selected element
        (selectedIndex,elem)=self.builder.get_object("foundFileTree").get_cursor()
        
        # get the metadatas of the selected element
        metadataStr=self.treestore[selectedIndex.to_string()][METADATA_INDEX]
        modMetadataStr=self.treestore[selectedIndex.to_string()][MOD_METADATA_INDEX]
        
        # if we don't have metadata, we are on a directory element
        if(metadataStr == None):
            self.__displayCommonMetadata(selectedIndex.to_string())
        else:
            mapMetadata=self.__transformInMap(metadataStr)
            mapModMetadata=self.__transformInMap(modMetadataStr)
            self.__displayMetadata(selectedIndex.to_string(), mapMetadata, mapModMetadata, False)
          
          
    # Display the metadata of the selected element in the right panel
    def __displayMetadata(self, index, metadataMap, modMetadataMap, directory):
        
        # get the metadata displayed grid 
        grid=self.builder.get_object("metadata_grid")
        
        # remove previous displayed metadatas
        for child in grid.get_children():
            grid.remove( child )
        
        grid.set_visible(True)
        
        i=1
        for key,value in sorted(metadataMap.iteritems()):
            
            # label with the name of the metadata
            label=Gtk.Label(label=key,visible=True)
            label.modify_font(Pango.FontDescription("bold 10"))
            label.set_max_width_chars(20)
            label.set_line_wrap(True)
            grid.attach(label,1,i,1,1)
            
            # label with the original value of the metadata
            label=Gtk.Label(visible=True,margin_left=10)
            if (metadataMap[key] != False):
                label.set_label(metadataMap[key])
            label.set_max_width_chars(20)
            label.set_line_wrap(True)
            label.modify_font(Pango.FontDescription("10"))
            grid.attach(label,2,i,1,1)
            
            # entry with the modified value of the metadata
            entry=Gtk.Entry(visible=True,margin_left=10)
            entry.set_name("entry_"+key)
            if (key in modMetadataMap and modMetadataMap[key] != False):
                entry.set_text(modMetadataMap[key])
            if ( not directory):
                entry.connect( 'changed', self.onChangeMetadata, (index,key))
            grid.attach(entry,3,i,1,1)
            
            i+=1
    
        
    # start the search in a directory
    def __startSearchThread(self,path):
        print "Start search in directory : "+path
        try:
            rootNode=self.treestore.append(None,[path.split("/")[-1],path,None,None])
            self.__scanFolder(path,rootNode) 
        except Exception as e:
            print("Exception during scan folder : %s" % e)
        finally:
            print "Search end"
            self.builder.get_object("progressGrid").set_visible(False)
            self.builder.get_object("spinner1").stop()
            self.builder.get_object("filechooserbutton1").set_sensitive(True)
        
        
if __name__ == '__main__':
    app = Application()
    Gtk.main()




