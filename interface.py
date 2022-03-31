# External libraries
from PyQt5 import QtCore, Qt, QtWidgets, QtGui
from functools import partial
import random
import vtk
from PIL import Image
import vtkplotlib as vpl
# Project files
import vtk_actors
from helper_functions import getLabelColor, computeCamPos, getEmptyImage
from data_class import project_data
from export_dataset import exportLandmarkDataset, exportMaskDatasetAsNumpyArray, exportTextLabelDataset
import time

#### Button functions
def exportDataset(self):
    folder_dir = Qt.QFileDialog.getExistingDirectory(self, 'Export dataset to:', 'c:\\')   
    if self.project_data.data['label_type'] == 'Text label':
        exportTextLabelDataset(folder_dir, self.project_data)
    elif self.project_data.data['label_type'] == 'Landmark label':
        exportLandmarkDataset(folder_dir, self.project_data)
    elif self.project_data.data['label_type'] == 'Mask label':
        exportMaskDatasetAsNumpyArray(folder_dir, self.project_data)

def createProj(self):
    #Create Project Database
    self.parent.project_data = project_data()
    self.parent.project_data.data['project_name'] = self.line_edit_proj_name.text()
    self.parent.project_data.data['label_type'] = self.combobox_label_selection.currentText()
    print("Combobox: ", self.combobox_label_selection.currentText())
    self.parent.project_data.data['color_mode'] = self.combobox_image_channels.currentText()
    
    #Create Project Database
    self.project_data = project_data()
    
    predefined_labels = []
    for x in range(self.list_predefined_labels.count()):
        predefined_labels.append(self.list_predefined_labels.item(x).text())
    
    self.parent.project_data.data['predefined_labels'] = predefined_labels
    
    # Try cleanup of old actors 
    try: 
        cleanupActorsLandmarkLabel(self.parent)
    except: 
        pass
    
    try: 
        cleanupActorsMaskLabel(self.parent)
    except: 
        pass
    
    # Refresh label selection in main window
    if self.parent.project_data.data['label_type'] == 'Mask label':
        initActorsMaskLabel(self.parent)
    
    if self.parent.project_data.data['label_type'] == 'Landmark label':
        initActorsLandmarkLabel(self.parent)
    
    self.parent.button_choose_image_directory.setText('Import image data')   
    self.parent.list_existing_labels.clear()
    
    updateGUIImageList(self.parent)
    updateComboboxPredefLabels(self.parent)
    showButtons(self.parent)
    updateAddLabelButton(self.parent)
    
    empty_img = getEmptyImage()
    self.parent.renderWindow.SetInputData(empty_img)  
    self.parent.iren.Initialize()
    self.parent.iren.Start()  
    
    self.close()

def loadImageData(self):
    folder_dir = Qt.QFileDialog.getExistingDirectory(self, 'Open file', 'c:\\')   
    self.project_data.loadNewImages(folder_dir)
    
    img_list = self.project_data.getImageList()
    img_list = sorted(img_list) 
   
    #updateGUIImageList(self)

    #render first image of img_list
    image_path = self.project_data.data['img_list_ordered'][0]
    vtk_image = getVTKImage(self, image_path)
    vtkChangeImageOperations(self, vtk_image)
    
    # Change text of button
    self.button_choose_image_directory.setText("Update image data")
    
    # Done after image switch
    updateUINewImage(self)
    
def addLabelToImage(self):
    label_combobox = self.combobox_label_selection.currentText()
    
    img_name = self.project_data.getCurrImg()
    if self.project_data.data['label_type'] != "Text label":
        coords = self.landmark_pos
        self.project_data.addLabel(label_combobox, img_name, coords)
    else: 
        self.project_data.addLabel(label_combobox, img_name)
    
    self.landmark_pos = []

    #Update GUI
    updateGUIImageList(self)
    updateUINewImage(self)
    updateImageLabelsAfterLabelChange(self)
    
def removeImageLabel(self):
    label_id = self.list_existing_labels.currentItem().value
    img_name = self.project_data.getCurrImg()
    self.project_data.removeLabelById(img_name, label_id)
    
    #Update GUI
    #updateGUIImageList(self)
    updateUINewImage(self)
    updateImageLabelsAfterLabelChange(self)
    

def show_selected_img(self):
    curr_img_name = self.list_img_names.currentItem().text()
    self.project_data.data['img_counter'] = self.list_img_names.currentRow() 
    if "✘" in curr_img_name:
        curr_img_name = curr_img_name[1:]

    updateUINewImage(self)
    vtk_image = getVTKImage(self, curr_img_name)
    vtkChangeImageOperations(self, vtk_image)
    
    
def expand_tree_side(self):
    self.tree.resizeColumnToContents(0)

def go_to_image(self):
    curr_img_name = self.tree.currentItem().text(0)
    curr_img_index = self.project_data.getImgIndex(curr_img_name)
    self.project_data.data['img_counter'] = curr_img_index
    
    updateUINewImage(self)
    vtk_image = getVTKImage(self, curr_img_name)
    vtkChangeImageOperations(self, vtk_image)
    
   
def showNextImage(self):    
    self.project_data.data['img_counter'] = self.project_data.data['img_counter'] + 1        
    if self.project_data.data['img_counter'] >= len(self.project_data.data['img_list_ordered']):
        self.project_data.data['img_counter'] = 0     
    
    updateUINewImage(self)
    next_img_name = self.project_data.getCurrImg()
    vtk_image = getVTKImage(self, next_img_name)
    vtkChangeImageOperations(self, vtk_image)

    
def showPreviousImage(self):
    self.project_data.data['img_counter'] = self.project_data.data['img_counter'] - 1        
    if self.project_data.data['img_counter'] < 0 :
        self.project_data.data['img_counter'] = len(self.project_data.data['img_list_ordered'])-1 

    updateUINewImage(self)         
    prev_img_name = self.project_data.getCurrImg()        
    vtk_image = getVTKImage(self, prev_img_name)
    vtkChangeImageOperations(self, vtk_image)
    vtkChangeImageOperations(self, vtk_image)
    

def predef_label_changed(self):
    label_combobox = self.combobox_label_selection.currentText()
    try: 
        new_color = getLabelColor(self.project_data.data['predefined_labels'], 
                                  self.project_data.data['color_list'], 
                                  label_combobox)
        if self.project_data.data['label_type'] == 'Landmark label':
            cap_actor = self.captionActor
        elif self.project_data.data['label_type'] == 'Mask label':
            cap_actor = self.captionActors[0]
            self.current_line_actor.GetProperty().SetColor(new_color)
            self.current_glyph_actor.GetProperty().SetColor(new_color)
        
        cap_actor.SetCaption('New label: ' + label_combobox)
        cap_actor.GetCaptionTextProperty().SetColor(new_color)
    except:
        pass


#### Update VTK objects
def initActorsMaskLabel(self):
    font_size = self.project_data.data['label_captions_font_size']
    ## Live actor mask label = Caption actor + line actor + glyphs actor
    # Live live caption actor
    self.captionActor = vtk_actors.createCaptionActors(1, font_size, visibility=True)[0]
    # Create live line actors
    self.current_line_actor = vtk_actors.createCurrentActorLines()
    self.mapper_lines = self.current_line_actor.GetMapper()
    # Glyph live actors
    self.current_glyph_actor, self.glyph2D = vtk_actors.createGlyphActor()
    ## Pre-existing labels: list of line actors
    self.line_actors = []
    # Landmark positions 
    self.landmark_pos = []

def cleanupActorsMaskLabel(self):
    
    self.ren.RemoveActor(self.captionActor)
    self.ren.RemoveActor(self.current_line_actor)
    self.ren.RemoveActor(self.current_glyph_actor)
    for old_line_actors in self.line_actors:
        self.ren.RemoveActor(old_line_actors)
    
def initActorsLandmarkLabel(self):        
    font_size = self.project_data.data['label_captions_font_size']
    self.captionActor = vtk_actors.createCaptionActors(1, font_size)[0]   
    self.captionActors = []
    self.landmark_pos = []
    
def cleanupActorsLandmarkLabel(self):
    self.ren.RemoveActor(self.captionActor)
    for caption_actor in self.captionActors:
        self.ren.RemoveActor(caption_actor)

def updateExistingLandmarkLabels(self):
    img_name = self.project_data.getCurrImg()
    label_list = self.project_data.getLabelList(img_name)
    font_size = self.project_data.data['label_captions_font_size']
    # First create caption actors!
    self.captionActors = vtk_actors.createCaptionActors(len(label_list), font_size, visibility=True)
    for i, label in enumerate(label_list, start=0): 
        rgb_color = getLabelColor(self.project_data.data['predefined_labels'], self.project_data.data['color_list'], label['label'])
        self.captionActors[i].SetCaption(label['label'])
        self.captionActors[i].SetAttachmentPoint(label['coords'][0], label['coords'][1], 0)
        self.captionActors[i].GetCaptionTextProperty().SetColor(rgb_color)
        self.ren.AddActor( self.captionActors[i] )
    self.iren.Initialize()
    self.iren.Start()  

def updateImageLabelsAfterLabelChange(self):
    # Clean up
    if self.project_data.data['label_type'] == 'Mask label': 
        cleanupActorsMaskLabel(self)
    if self.project_data.data['label_type'] == 'Landmark label':
        cleanupActorsLandmarkLabel(self)
        
    if self.project_data.data['label_type'] == 'Landmark label':
        vtk_actors.addCurrentLandmarkActor(self)
        if self.checkbox_plot_all_labels.isChecked():
            updateExistingLandmarkLabels(self)   
    if self.project_data.data['label_type'] == 'Mask label':
        vtk_actors.addCurrentMaskLabelActors(self)
        if self.checkbox_plot_all_labels.isChecked():
            updateExistingMaskLabels(self)
            
    self.iren.Initialize()
    self.iren.Start()  

def updateExistingMaskLabels(self):
    img_name = self.project_data.getCurrImg()
    label_list = self.project_data.getLabelList(img_name)
    predef_labels = self.project_data.data['predefined_labels']
    color_list = self.project_data.data['color_list']
    self.line_actors = vtk_actors.createMaskLabelActors(label_list, self.landmark_pos, predef_labels, color_list )
    for lineActor in self.line_actors:
        self.ren.AddActor( lineActor )
    self.iren.Initialize()
    self.iren.Start()  
 
def vtkChangeImageOperations(self, vtk_image):
    self.img_dims =  vtk_image.GetDimensions()
    self.img_spacing = vtk_image.GetSpacing()
    self.img_orig = vtk_image.GetOrigin()
    self.ren.GetActors().RemoveAllItems()
    
    self.landmark_pos = []
    
    if self.project_data.data['label_type'] == 'Landmark label':
        cleanupActorsLandmarkLabel(self)
        if self.checkbox_plot_all_labels.isChecked():
            updateExistingLandmarkLabels(self)
            
    if self.project_data.data['label_type'] == 'Mask label':
        cleanupActorsMaskLabel(self)
        if self.checkbox_plot_all_labels.isChecked():
            updateExistingMaskLabels(self)
            
            
    camera = self.ren.GetActiveCamera()
    camera_pos = computeCamPos(vtk_image.GetOrigin(), vtk_image.GetDimensions(), 
                  vtk_image.GetSpacing(), camera.GetViewAngle())
    camera.SetFocalPoint(camera_pos[0], camera_pos[1], 0)
    camera.SetPosition(0, 0, 0)
    camera.SetPosition(camera_pos[0], camera_pos[1], camera_pos[2])
    self.renderWindow.SetInputData(vtk_image)  
    self.iren.Initialize()
    self.iren.Start()  
    
def getVTKImage(self, image):
    image_path = self.project_data.data["folder_directory"] + image

    with Image.open(image_path) as im:
        if self.project_data.data['color_mode'] == "RGB":
            im = im.convert("RGB")
        else:
            im = im.convert("L")
        vtk_image = vpl.image_io.as_vtkimagedata(im, ndim=None)

    return vtk_image


    

#### Update main window QT elements
def showButtons(self):
    for i in self.findChildren(Qt.QPushButton):
        i.show()          
    for i in self.findChildren(Qt.QCheckBox):
        i.show()        
    for i in self.findChildren(Qt.QSlider):
        i.show() 
    for i in self.findChildren(Qt.QComboBox):
        i.show() 
    for i in self.findChildren(Qt.QLineEdit):
        i.show() 
    for i in self.findChildren(Qt.QLabel):
        i.show()    
    for i in self.findChildren(Qt.QListWidget):
        i.show()    
    for i in self.findChildren(Qt.QTreeWidget):
        i.show()
    for i in self.findChildren(Qt.QFrame):
        i.show()
        
def updateAddLabelButton(self):
    label_type = self.project_data.data['label_type']
    if label_type == "Text label":
        self.button_create_label.setText('Add label')      
    elif label_type == "Landmark label":
        self.button_create_label.setText('Add landmark label')  
    elif label_type == "Mask label":
        self.button_create_label.setText('Add mask label')  
def updateComboboxPredefLabels(self):
    if len(self.project_data.data['images']) > 0:
        curr_img = self.project_data.getCurrImg()
        label_list_label_dicts = self.project_data.getLabelList(curr_img)
        list_labels = [label_dict['label'] for label_dict in label_list_label_dicts]
    else:
        # When no images are loaded yet
        list_labels = []
    self.combobox_label_selection.clear()
    for text_label_item in self.project_data.data['predefined_labels']:
        if not text_label_item in list_labels:
            self.combobox_label_selection.addItem(text_label_item)

def updateExistingLabelsList(self):
    img_name = self.project_data.getCurrImg()
    print("img name of curr img: ", img_name)
    self.list_existing_labels.clear()
    for label_dict in self.project_data.getLabelList(img_name):        
        #Create colored ◼-item
        color_rgb = getLabelColor(self.project_data.data['predefined_labels'], self.project_data.data['color_list'], label_dict['label'])
        html_str_1 = '<font style="color: rgb('
        html_str_2 = str(int(color_rgb[0]*255)) +','+str(int(color_rgb[1]*255)) +','+str(int(color_rgb[2]*255))
        html_str_3 = ')"> ◼ </font> '
        html_str_4 = label_dict['label']
        if self.project_data.data['label_type'] != 'Text label':
            str_complete = html_str_1+html_str_2+html_str_3+html_str_4
        else: 
            str_complete = html_str_4
        delegate = HTMLDelegate(self.list_existing_labels)
        self.list_existing_labels.setItemDelegate(delegate)
        item = QtWidgets.QListWidgetItem(str_complete)
        # Set label id as private value
        item.value = label_dict['label_id']
        self.list_existing_labels.addItem(item)   
           

def updateUINewImage(self):
    # Set label section
    tic1 = time.time()
    updateExistingLabelsList(self)
    tic2 = time.time()
    updateImageTree(self)
    tic3 = time.time()
    updateComboboxPredefLabels(self)
    tic4 = time.time()
    updateGUIImageList(self)
    
    

    
    # Set list item
    curr_img_name = self.project_data.data['img_list_ordered'][self.project_data.data['img_counter']]
    """
    try: 
        items = self.list_img_names.findItems(curr_img_name, QtCore.Qt.MatchExactly)
        self.list_img_names.setCurrentItem( items[0] )
    except: 
        items = self.list_img_names.findItems("✘" + curr_img_name, QtCore.Qt.MatchExactly)
        self.list_img_names.setCurrentItem( items[0] )
    """
    tic5 = time.time()
    self.list_img_names.setCurrentRow( self.project_data.data['img_counter'] )
    
    tic6 = time.time()
    
    if curr_img_name in self.project_data.data["expert_review_list"]:
        self.checkbox_expert_review.setChecked(True)
    else: 
        self.checkbox_expert_review.setChecked(False)
    
    tic7 = time.time()
    
    print("UpdateExistingLabelList: ", tic2 - tic1)
    print("updateImageTree: ", tic3 - tic2)
    print("updateComboboxPredefLabels: ", tic4 - tic3)
    print("updateGUIImageList: ", tic5 - tic4)
    print("Set current row: ", tic6 - tic5)
    print("Expert review: ", tic7 - tic6)
    print("----------------------")

def updateImageTree(self):
    items = []
    item_labeled_img = Qt.QTreeWidgetItem(['Labeled image data'])
    item_unlabeled_img = Qt.QTreeWidgetItem(['Unlabeled image data'])
    expert_review_list_imgs = Qt.QTreeWidgetItem(['Expert review needed'])
    for img_key in self.project_data.data['images']:
        if len( self.project_data.data['images'][img_key]['labels'] ) == 0:
            child = Qt.QTreeWidgetItem([img_key])
            item_unlabeled_img.addChild(child)
        else:
            child = Qt.QTreeWidgetItem([img_key])
            item_labeled_img.addChild(child)
    for expert_review_img in self.project_data.data['expert_review_list']:
        child = Qt.QTreeWidgetItem([expert_review_img])
        expert_review_list_imgs.addChild(child)
    item_project_details = Qt.QTreeWidgetItem(['Project details'])
    child_proj_name = Qt.QTreeWidgetItem(['Project name: ' + self.project_data.data['project_name']])
    item_project_details.addChild(child_proj_name)
    child_label_type = Qt.QTreeWidgetItem(['Label type: ' + self.project_data.data['label_type']])
    item_project_details.addChild(child_label_type)
    child_label_type = Qt.QTreeWidgetItem(['Color mode: ' + self.project_data.data['color_mode']])
    item_project_details.addChild(child_label_type)
    total_count_imgs = str(len(self.project_data.getImageList(False)))
    total_count_labeled_imgs = str(len(self.project_data.getImageList(True)))
    child_total_image_count = Qt.QTreeWidgetItem(['Images total: ' + total_count_imgs])
    item_project_details.addChild(child_total_image_count)
    child_labeled_image_count = Qt.QTreeWidgetItem(['Labeled images: ' + total_count_labeled_imgs])
    item_project_details.addChild(child_labeled_image_count)
    child_total_number_labels = Qt.QTreeWidgetItem(['Total count labels: ' + str(len(self.project_data.returnAllLabels()))])
    item_project_details.addChild(child_total_number_labels)
    items.append(item_project_details)
    items.append(item_labeled_img)
    items.append(item_unlabeled_img)
    items.append(expert_review_list_imgs)
    root = self.tree.invisibleRootItem()
    child_count = root.childCount()
    expanded_list  = []
    for i in range(child_count):
        item = root.child(i)
        expanded_list.append(item.isExpanded())
    self.tree.clear()
    self.tree.insertTopLevelItems(0, items)
    root = self.tree.invisibleRootItem()
    child_count = root.childCount()
    if expanded_list != []:
        for i in range(child_count):
            item = root.child(i)
            item.setExpanded (expanded_list[i])

def add2ExpertReviewList(self):
    curr_img = self.project_data.getCurrImg()
    if self.checkbox_expert_review.isChecked():
        if curr_img not in self.project_data.data['expert_review_list']:
            self.project_data.data['expert_review_list'].append(curr_img)
    else:
        self.project_data.data['expert_review_list'] = [img_name for img_name in self.project_data.data['expert_review_list'] if img_name  != curr_img]
    updateImageTree(self)
    
#### Subwindow button functions
def addLabelToPredefinedLabelsNewProj(self):
    le_text = self.line_edit_predefined_label_name.text()
    self.line_edit_predefined_label_name.clear()
    self.list_predefined_labels.addItem(le_text)
    # Expand existing color list if necessary
    len_predef_labels = self.list_predefined_labels.count()
    len_color_list = len(self.parent.project_data.data['color_list'])
    if len_predef_labels > len_color_list:
        # Add random colors to color list
        random_color = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
        self.parent.project_data.data['color_list'].append(random_color)
   
def addLabelToPredefinedLabelsEditPredef(self):
    le_text = self.line_edit_new_predefined_label_name.text()
    if le_text != "":
        self.line_edit_new_predefined_label_name.clear()
        self.list_predefined_labels.addItem(le_text)
        self.parent.project_data.data['predefined_labels'].append(le_text)
        # Update predef label combobox in main window
        updateComboboxPredefLabels(self.parent)
        # Expand color list if necessary
        len_predef_labels = len( self.parent.project_data.data['predefined_labels'])
        len_color_list = len(self.parent.project_data.data['color_list'])
        if len_predef_labels > len_color_list:
            # Add random colors to color list
            random_color = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
            self.parent.project_data.data['color_list'].append(random_color)

def removePredefinedLabel(self):
    delete_item_name = self.list_predefined_labels.currentItem().text()
    self.parent.project_data.data['predefined_labels'] = [elem for elem in self.parent.project_data.data['predefined_labels'] if elem != delete_item_name]
    # Update list in subwindow
    self.list_predefined_labels.clear()
    for predef_label in self.parent.project_data.data['predefined_labels']:
        self.list_predefined_labels.addItem(predef_label)
    # Clear dataset of old label 
    self.parent.project_data.removeLabelByPredef( delete_item_name)
    # Update predef label combobox in main window
    updateComboboxPredefLabels(self.parent)
    updateImageLabelsAfterLabelChange(self.parent)
    
def changeLabelName(self):
    old_label = self.parent.list_predefined_labels.currentItem().text()
    new_label = self.line_edit_new_label_name.text()
    # Change in preselected label list
    for index, preselected_label in enumerate(self.parent.parent.project_data.data['predefined_labels'], start=0):
        if preselected_label == old_label:
            self.parent.parent.project_data.data['predefined_labels'][index] = new_label
    # Refresh label selction in sub window 
    self.parent.list_predefined_labels.clear()
    for predef_label in self.parent.parent.project_data.data['predefined_labels']:
        self.parent.list_predefined_labels.addItem(predef_label)
    #Change all old labels in existing dataset to new label
    self.parent.parent.project_data.changeLabel(old_label, new_label)
    # Refresh label list in main window
    updateComboboxPredefLabels(self.parent.parent)
    updateImageLabelsAfterLabelChange(self.parent.parent)
    updateExistingLabelsList(self.parent.parent)
    self.close()
    
    
#### Init of UI PyQT objects
def initLabelSection(self, label_type):
    self.label_current_labels_summary = Qt.QLabel(self)        
    self.label_current_labels_summary.setText("Image labels: ")   
    self.label_current_labels_summary.setSizePolicy(self.sizePolicy)
    self.label_current_labels_summary.setStyleSheet("font-style: italic; color: grey ")
    self.label_current_labels_summary.hide()
    self.label_add_label = Qt.QLabel(self)        
    self.label_add_label.setText("Add new label: ")   
    self.label_add_label.setSizePolicy(self.sizePolicy)
    self.label_add_label.setStyleSheet("font-style: italic; color: grey")
    self.label_add_label.hide()
    self.list_existing_labels = Qt.QListWidget()    
    self.list_existing_labels.setFixedWidth(200)
    self.list_existing_labels.setSizePolicy(self.sizePolicy)
    self.list_existing_labels.hide()
    self.combobox_label_selection = Qt.QComboBox()  
    # Load pre-selected labels
    for text_label_item in self.project_data.data['predefined_labels']:
        self.combobox_label_selection.addItem(text_label_item)
    if len(self.project_data.data['predefined_labels']) > 0:
        self.combobox_label_selection.model().item(0).setEnabled(False)    
    self.combobox_label_selection.setFixedWidth(200)
    self.combobox_label_selection.setSizePolicy(self.sizePolicy)
    self.combobox_label_selection.currentIndexChanged.connect(partial(predef_label_changed, self))
    self.combobox_label_selection.hide()
    self.button_create_label = Qt.QPushButton('', self) 
    self.button_create_label.clicked.connect(partial(addLabelToImage, self))  
    self.button_create_label.setFixedWidth(200)
    self.button_create_label.setSizePolicy(self.sizePolicy)
    self.button_create_label.hide()
    self.button_edit_predefined_label_list = Qt.QPushButton('Edit label class list', self)  
    self.button_edit_predefined_label_list.clicked.connect(self.editPredefLabels)  
    self.button_edit_predefined_label_list.setFixedWidth(200)
    self.button_edit_predefined_label_list.setSizePolicy(self.sizePolicy)
    self.button_edit_predefined_label_list.hide()
    self.button_remove_label = Qt.QPushButton('Remove label', self)           
    self.button_remove_label.clicked.connect(partial(removeImageLabel, self))  
    self.button_remove_label.setFixedWidth(200)
    self.button_remove_label.setSizePolicy(self.sizePolicy)
    self.button_remove_label.hide()
    self.checkbox_plot_all_labels = Qt.QCheckBox("Plot all image labels")
    self.checkbox_plot_all_labels.setChecked(True)
    self.checkbox_plot_all_labels.stateChanged.connect(partial(updateImageLabelsAfterLabelChange, self))
    self.checkbox_plot_all_labels.hide()
    
def initImageSection(self):
    self.list_img_names = Qt.QListWidget()    
    self.list_img_names.setFixedWidth(200)
    self.list_img_names.setSizePolicy(self.sizePolicy)
    self.list_img_names.itemDoubleClicked.connect(partial(show_selected_img, self)) 
    self.list_img_names.hide()
    
    self.button_choose_image_directory = Qt.QPushButton('Import image data', self)        
    self.button_choose_image_directory.clicked.connect(partial(loadImageData, self))    
    self.button_choose_image_directory.setFixedWidth(200)
    self.button_choose_image_directory.setSizePolicy(self.sizePolicy)
    self.button_choose_image_directory.hide()
    
    self.button_next_image = Qt.QPushButton('', self)
    self.button_next_image.setIcon(self.style().standardIcon(Qt.QStyle.SP_MediaSkipForward))    
    self.button_next_image.clicked.connect(partial(showNextImage, self) )  
    self.button_next_image.setSizePolicy(self.sizePolicy)
    self.button_next_image.hide()
    
    self.button_previous_image = Qt.QPushButton('', self)
    self.button_previous_image.setIcon(self.style().standardIcon(Qt.QStyle.SP_MediaSkipBackward))    
    self.button_previous_image.clicked.connect(partial(showPreviousImage, self))
    self.button_previous_image.setSizePolicy(self.sizePolicy)
    self.button_previous_image.hide()
    
    self.button_remove_image = Qt.QPushButton('Remove image', self)
    self.button_remove_image.clicked.connect(partial(removeImageFromDataset, self))
    self.button_remove_image.setSizePolicy(self.sizePolicy)
    self.button_remove_image.hide()
    
    self.checkbox_expert_review = Qt.QCheckBox("Expert review needed")
    self.checkbox_expert_review.setChecked(False)
    self.checkbox_expert_review.stateChanged.connect(partial(add2ExpertReviewList, self))
    self.checkbox_expert_review.hide()
   
    
    self.hl_image_navigation = Qt.QHBoxLayout() 
    self.hl_image_navigation.addWidget(self.button_previous_image)
    self.hl_image_navigation.addWidget(self.button_next_image)


def removeImageFromDataset(self):
    curr_img = self.project_data.getCurrImg()
    self.project_data.removeImage(curr_img)
    
    #updateGUIImageList(self)
    
    # Insert removed image into deleted image list. This way the removed images wont get 
    # re-uploaded when dataset is updated new images
    self.project_data.data['deleted_images'].append(curr_img)
    
    updateUINewImage(self)
    next_img_name = self.project_data.getCurrImg()
    vtk_image = getVTKImage(self, next_img_name)
    vtkChangeImageOperations(self, vtk_image)
    
    
def saveProject(self):
    # Def path
    project_path_name, _ = Qt.QFileDialog.getSaveFileName(self, \
     "QFileDialog.getSaveFileName()","","Input Files(*.json)")      
    
    self.project_data.saveDataset(project_path_name)
    
def updateGUIImageList(self):
    # Clear image list
    self.list_img_names.clear()
    
    # Update image list
    for image_name in self.project_data.data['img_list_ordered']:
        if len(self.project_data.data['images'][image_name]['labels']) > 0:
            self.list_img_names.addItem("✘" + image_name)
        else:
            self.list_img_names.addItem(image_name)

def loadProject(self):
    path_name, _ = Qt.QFileDialog.getOpenFileName(self, 'Open file')
    self.project_data.loadDataset(path_name)
    self.loadProjectMenu()

def loadProjectContinue(self):
    showButtons(self)
    
    # Try cleanup of old actors 
    try: 
        cleanupActorsLandmarkLabel(self)
    except: 
        pass
    
    try: 
        cleanupActorsMaskLabel(self)
    except: 
        pass
    
    #updateGUIImageList(self)
      
    first_img = self.project_data.data['img_list_ordered'][self.project_data.data['img_counter']]
    
    #render first image of img_list
    #image_path = self.project_data.data['images'][first_img]['directory_path'] + "/" + first_img
    if self.project_data.data['label_type'] == 'Mask label':
        initActorsMaskLabel(self)
        
    if self.project_data.data['label_type'] == 'Landmark label':
        initActorsLandmarkLabel(self)

    # Change text of button
    self.button_choose_image_directory.setText("Update image data")
    
    updateUINewImage(self)
    vtk_image = getVTKImage(self, first_img)
    vtkChangeImageOperations(self, vtk_image)
    
    updateAddLabelButton(self)
    
def initProject(self):
    initProjectSection(self)
    initLabelSection(self, self.project_data.data['label_type'])
    initImageSection(self)

def correctImageDirectory(self):
    loadProjectContinue(self.parent)
    self.close()
    
def changeImageDirectory(self, name):
    folder_dir = Qt.QFileDialog.getExistingDirectory(self, 'Select correct image directory', 'c:\\')  
    
    self.check_img_src_2_label.setText(folder_dir)
    
    self.parent.project_data.data["folder_directory"] = folder_dir + "/"
  
    
def initProjectSection(self):
    self.label_placeholder = Qt.QLabel()
    self.dummy_placeholder = Qt.QLabel()
 
    #self.label_project_section.setText("--------- Project settings ------------------------------------------")
     
    self.button_new_project = Qt.QPushButton('New project', self)           
    self.button_new_project.clicked.connect(self.newProject)  
    self.button_new_project.setFixedWidth(200)
    
    self.button_load_project = Qt.QPushButton('Load project', self)           
    self.button_load_project.clicked.connect(partial(loadProject, self))  
    self.button_load_project.setFixedWidth(200)
    
    self.button_save_project = Qt.QPushButton('Save project', self)           
    self.button_save_project.clicked.connect(partial(saveProject, self))     
    self.button_save_project.setFixedWidth(200)
    
    self.button_export_project_CSV = Qt.QPushButton('Export dataset', self)           
    self.button_export_project_CSV.clicked.connect(partial(exportDataset, self))   
    self.button_export_project_CSV.setFixedWidth(200)
    
    #self.label_textbox_project_settings = Qt.QLabel()
    #self.label_textbox_project_settings.setText("-")
    #self.label_textbox_project_settings.setStyleSheet("background-color: rgba(255, 255, 255, 100%)")
    
    self.tree = Qt.QTreeWidget()
    self.tree.setColumnCount(1)
    self.tree.setHeaderLabels(["Project summary"])
    self.tree.itemClicked.connect(partial(expand_tree_side, self)) 
    self.tree.itemDoubleClicked.connect(partial(go_to_image, self)) 
    self.tree.setSizePolicy(self.sizePolicy)
    self.tree.resizeColumnToContents(0)
    self.tree.hide()
    
def initNewProjDiag(self):
    self.line_edit_proj_name_label = Qt.QLabel()
    self.line_edit_proj_name_label.setText("Enter project name: ")
    
    self.line_edit_proj_name = Qt.QLineEdit()
    
    self.label_label_type = Qt.QLabel()
    self.label_label_type.setText("Choose label type: ")
    
    self.combobox_label_selection = Qt.QComboBox()  
    self.combobox_label_selection.addItem("Text label")
    self.combobox_label_selection.addItem("Landmark label")
    self.combobox_label_selection.addItem("Mask label")
    
    self.label_image_channels = Qt.QLabel()
    self.label_image_channels.setText("Load images as ... ")
    
    self.combobox_image_channels = Qt.QComboBox()  
    self.combobox_image_channels.addItem("Grayscale")
    self.combobox_image_channels.addItem("RGB")
    
    self.button_create_project = Qt.QPushButton('Create', self)  
        
    self.button_create_project.clicked.connect(partial(createProj, self))  
    
    self.label_enter_predefined_text_label = Qt.QLabel()
    self.label_enter_predefined_text_label.setText("Label classes: ")
    
    self.button_add_predefined_text_label = Qt.QPushButton('Add new label class', self) 
    self.button_add_predefined_text_label.clicked.connect(partial(addLabelToPredefinedLabelsNewProj, self)) 
    self.line_edit_predefined_label_name = Qt.QLineEdit()
    
    self.list_predefined_labels = Qt.QListWidget()    
    self.list_predefined_labels.setFixedHeight(60)
    self.list_predefined_labels.setFixedWidth(200)
    #self.list_predefined_labels.setSizePolicy(self.sizePolicy)
    #self.list_predefined_labels.itemDoubleClicked.connect(partial(show_selected_img, self)) 
 
    self.new_proj_grid = Qt.QGridLayout()  
    self.new_proj_grid.addWidget(self.line_edit_proj_name_label, 1, 1, 1, 1)
    self.new_proj_grid.addWidget(self.line_edit_proj_name, 1, 2, 1, 1)
    self.new_proj_grid.addWidget(self.label_label_type, 2, 1, 1, 1)
    self.new_proj_grid.addWidget(self.combobox_label_selection, 2, 2, 1, 1)
    
    self.new_proj_grid.addWidget(self.label_image_channels, 3, 1, 1, 1)
    self.new_proj_grid.addWidget(self.combobox_image_channels, 3, 2, 1, 1)
  
    self.new_proj_grid.addWidget(self.label_enter_predefined_text_label,  4, 1, 1, 1)
    self.new_proj_grid.addWidget(self.line_edit_predefined_label_name,  5, 2, 1, 1)
    self.new_proj_grid.addWidget(self.button_add_predefined_text_label,  6, 2, 1, 1)
    self.new_proj_grid.addWidget(self.list_predefined_labels,  5, 1, 2, 1)
    self.new_proj_grid.addWidget(self.button_create_project,  7, 1, 1, 1)
    
def initChangePreselectLabelName(self):
    self.label_change_label_name = Qt.QLabel()
    self.label_change_label_name.setText("New name for selected class label: ")
    
    self.line_edit_new_label_name = Qt.QLineEdit()
    
    self.button_change_label_name = Qt.QPushButton('Change label class name', self)  
    self.button_change_label_name.clicked.connect(partial(changeLabelName, self))  
    
    self.change_label_name_grid = Qt.QGridLayout()  
    self.change_label_name_grid.addWidget(self.label_change_label_name, 1, 1, 1, 1)
    self.change_label_name_grid.addWidget(self.line_edit_new_label_name, 2, 1, 1, 1)
    self.change_label_name_grid.addWidget(self.button_change_label_name, 2, 2, 1, 1)

def initPredefinedLabelsEditMenu(self):
    self.label_list_predefined_labels = Qt.QLabel()
    self.label_list_predefined_labels.setText("Label class list: ")
    
    self.line_edit_new_predefined_label_name = Qt.QLineEdit()
    
    self.button_add_predefined_text_label = Qt.QPushButton('Add label class', self) 
    self.button_add_predefined_text_label.clicked.connect(partial(addLabelToPredefinedLabelsEditPredef, self)) 
   
    self.button_remove_predefined_text_label = Qt.QPushButton('Remove', self) 
    self.button_remove_predefined_text_label.clicked.connect(partial(removePredefinedLabel, self)) 
    
    self.button_edit_predefined_text_label = Qt.QPushButton('Edit', self) 
    self.button_edit_predefined_text_label.clicked.connect(self.changePreselectLabelName) 
    
    self.list_predefined_labels = Qt.QListWidget()    
    self.list_predefined_labels.setFixedHeight(60)
    self.list_predefined_labels.setFixedWidth(200)
    for predef_label in self.parent.project_data.data['predefined_labels']:
        self.list_predefined_labels.addItem(predef_label)
        
    self.predefined_labels_edit_menu = Qt.QGridLayout()  
    self.predefined_labels_edit_menu.addWidget(self.label_list_predefined_labels, 1, 1, 1, 1)
    self.predefined_labels_edit_menu.addWidget(self.list_predefined_labels, 2, 1, 2, 2)
    self.predefined_labels_edit_menu.addWidget(self.button_remove_predefined_text_label, 2, 3, 1, 1)
    self.predefined_labels_edit_menu.addWidget(self.button_edit_predefined_text_label, 3, 3, 1, 1)

    self.predefined_labels_edit_menu.addWidget(self.line_edit_new_predefined_label_name,  4, 1, 1, 1)
    self.predefined_labels_edit_menu.addWidget(self.button_add_predefined_text_label,  4, 2, 1, 1)

def initLoadProjectMenu(self):
    self.check_img_src_1_label = Qt.QLabel()
    self.check_img_src_1_label.setText("Check image source directory: ")
    project_img_directory_path = self.parent.project_data.data['folder_directory']
    self.check_img_src_2_label = Qt.QLabel()
    self.check_img_src_2_label.setStyleSheet("background-color: white;")
    self.check_img_src_2_label.setText(project_img_directory_path)
    
    self.button_correct_img_directory = Qt.QPushButton('Correct', self) 
    self.button_correct_img_directory.clicked.connect(partial(correctImageDirectory, self)) 
    
    self.button_change_img_directory = Qt.QPushButton('Change image directoy', self) 
    self.button_change_img_directory.clicked.connect(partial(changeImageDirectory, self)) 
    
    self.load_project_menu = Qt.QGridLayout()  
    self.load_project_menu.addWidget(self.check_img_src_1_label, 1, 1, 1, 1)
    self.load_project_menu.addWidget(self.check_img_src_2_label, 2, 1, 1, 2)
    self.load_project_menu.addWidget(self.button_correct_img_directory, 3, 1, 1, 1)
    self.load_project_menu.addWidget(self.button_change_img_directory, 3, 2, 1, 1)
   
def initUI(self):
    """ 
    This function defines the architecture of the GUI and connects 
    the created QT widgets to the corresponding functions defined in this 
    file. The various QT objects are arranged along vertical and horizontal
    axes.   
    """ 
    self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
    self.sizePolicy.setRetainSizeWhenHidden(True)

    initProject(self)
    
    self.sep_line_1 = Qt.QFrame()
    self.sep_line_1.setFrameShape(Qt.QFrame.HLine)
    self.sep_line_1.setFrameShadow(Qt.QFrame.Sunken)
    self.sep_line_1.setSizePolicy(Qt.QSizePolicy.Minimum,Qt.QSizePolicy.Expanding)
    self.sep_line_1.setLineWidth(2)
    self.sep_line_1.hide()
    
    self.sep_line_2 = Qt.QFrame()
    self.sep_line_2.setFrameShape(Qt.QFrame.HLine)
    self.sep_line_2.setFrameShadow(Qt.QFrame.Sunken)
    self.sep_line_2.setSizePolicy(Qt.QSizePolicy.Minimum,Qt.QSizePolicy.Expanding)
    self.sep_line_2.setLineWidth(2)
    self.sep_line_2.hide()
    
    # Project area
    self.UI_grid = Qt.QGridLayout()  
    self.UI_grid.addWidget(self.button_new_project, 2, 1, 1, 1)
    self.UI_grid.addWidget(self.button_load_project, 3, 1, 1, 1)    
    self.UI_grid.addWidget(self.button_save_project, 4, 1, 1, 1)    
    self.UI_grid.addWidget(self.button_export_project_CSV, 5, 1, 1, 1)
    self.UI_grid.addWidget(self.tree, 2, 2, 4, 2)
    
    # Image area
    self.UI_grid.addWidget(self.sep_line_1, 7, 1, 1, 3)
    self.UI_grid.addWidget(self.button_choose_image_directory, 8, 2, 1, 1)
    self.UI_grid.addLayout(self.hl_image_navigation, 9, 2, 1, 1)
    self.UI_grid.addWidget(self.checkbox_expert_review, 10, 2, 1, 1)
    self.UI_grid.addWidget(self.button_remove_image, 11, 2, 1, 1)
    self.UI_grid.addWidget(self.list_img_names , 8, 1, 4, 3)
  
    # Label area
    self.UI_grid.addWidget(self.sep_line_2, 12, 1, 1, 3)
    self.UI_grid.addWidget(self.label_current_labels_summary, 13, 1, 1, 2)
    self.UI_grid.addWidget(self.label_add_label, 13, 2, 1, 1) 
    self.UI_grid.addWidget(self.list_existing_labels, 14, 1, 3, 1)  
    self.UI_grid.addWidget(self.button_remove_label, 17, 1, 1, 1)  
    self.UI_grid.addWidget(self.combobox_label_selection, 14, 2, 1, 1) 
    self.UI_grid.addWidget(self.button_create_label, 15, 2, 1, 1) 
    self.UI_grid.addWidget(self.button_edit_predefined_label_list, 16, 2, 1, 1)
    self.UI_grid.addWidget(self.checkbox_plot_all_labels, 17, 2, 1, 1)
    self.UI_grid.addWidget(self.label_placeholder, 18, 1, 1, 3)
    
    # Definition of the vertical and horizontal main axis    
    self.hl_main = Qt.QHBoxLayout()      
    self.frame.setLayout(self.hl_main)    
    
    # Set ratio of UI menu to image window
    self.UI_grid.setColumnStretch(1, 1)       
    self.UI_grid.setColumnStretch(2, 1)  
    self.UI_grid.setColumnStretch(3, 1) 
    
    # Alignment along horizontal main axis   
    self.hl_main.addLayout(self.UI_grid, stretch=1 )
    self.hl_main.addWidget(self.vtkWidget, stretch=2)
    

class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    """ This class is used as HTML delegate in the image label list. This way a colored box can 
    be placed next to the label. """
    def __init__(self, parent=None):
        super(HTMLDelegate, self).__init__(parent)
        self.doc = QtGui.QTextDocument(self)

    def paint(self, painter, option, index):
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        self.doc.setHtml(options.text)
        options.text = ""
        style = QtWidgets.QApplication.style() if options.widget is None \
            else options.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        if option.state & QtWidgets.QStyle.State_Selected:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.Text))
        textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, options, None)
        if index.column() != 0:
            textRect.adjust(5, 0, 0, 0)
        constant = 4
        margin = (option.rect.height() - options.fontMetrics.height()) // 2
        margin = margin - constant
        textRect.setTop(textRect.top() + margin)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(self.doc.idealWidth(), self.doc.size().height())    
        