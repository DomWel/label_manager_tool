import json
from datetime import datetime
import os

class project_data():
    def __init__(self):
        self.data = {
            'project_name': None,
            'images': {}, 
            'labels': [],
            'label_type': None, 
            'predefined_labels': [],
            'img_list_ordered': [], 
            'expert_review_list': [],
            'color_list': [[1,0,0],[0,1,0],[0,0,1],[1,1,0],[1,0,1],[0,1,1]],
            'img_counter': 0,
            'label_captions_font_size': 25,
            'folder_directory': None,
            'deleted_images': [],
            'color_mode': None}
        
    def returnAllLabels(self):
        label_list = [label for img in self.data['images'] for label in self.data['images'][img]['labels']]
        return label_list
    
    def getImgIndex(self, img):
        return self.data['img_list_ordered'].index(img)
    
    def getImageList(self, min_labels=0):
        img_list = []
        for key in sorted(self.data['images']):
            if min_labels != 0:
                if len(self.data['images'][key]['labels']) >= min_labels:
                    img_list.append(key)
            else:
                img_list.append(key)
        return img_list
    
    def check_img_list(self, img_list, images):
        bool(set(img_list) & set(images))
        
    def loadNewImages(self, folder_dir, include_subfolders=True):
        self.data["folder_directory"] = folder_dir+"/"
        span_folder_dir = len(self.data["folder_directory"])
        if include_subfolders:
            list_subdirectories = [x[0] for x in os.walk(folder_dir)]
            for subdirectory in list_subdirectories:
                for images in os.listdir(subdirectory): 
                    if (images.endswith(".png")) or (images.endswith(".jpg")):
                        img_list = self.getImageList()
                        image_path = subdirectory + '/' + images
                        image_path = image_path[span_folder_dir:]
                        if not (str(image_path) in img_list or str(image_path) in self.data['deleted_images']):  
                            self.data['images'][image_path] = {'labels': []}
        else:
            for images in os.listdir(folder_dir): 
                
                if (images.endswith(".png")) or (images.endswith(".jpg")):
                    img_list = self.getImageList()
                    if not self.check_img_list(img_list, images):  
                        img_list = self.getImageList()
                        image_path = subdirectory + '/' + images
                        image_path = image_path[span_folder_dir:]
                        if not (str(image_path) in img_list or str(image_path) in self.data['deleted_images']):  
                            self.data['images'][image_path] = {'labels': []}
            
    
        self.data['img_list_ordered'] = sorted(self.getImageList())
        
    def getCurrImg(self):
        return self.data['img_list_ordered'][self.data['img_counter']] 
        
    def loadDataset(self, project_path_name):
        with open(project_path_name, 'r') as f:
          data = json.load(f)
          self.data = data
        
        self.data['img_list_ordered'] = sorted(self.getImageList())
          
    def getLabelList(self, img_name):
        img_dict = self.data['images'][img_name]
        label_list = img_dict['labels']
        return label_list
    
    def removeLabelByPredef(self, predef_label_name):
        for img_key in self.data['images']:
            self.data['images'][img_key]['labels'] = \
                [label_dict for label_dict in self.data['images'][img_key]['labels'] if label_dict['label'] != predef_label_name]
            
    def changeLabel(self, old_label_name, new_label_name):
        for img_key in self.data['images']:
            for label_dict in self.data['images'][img_key]['labels']:
                if label_dict['label'] == old_label_name:
                    label_dict['label'] = new_label_name
                
    def removeLabelById(self, img_name, label_id):        
        self.data['images'][img_name]['labels'] = [item for item in self.data['images'][img_name]['labels'] if item['label_id'] != label_id]
    
    def saveDataset(self, project_path_name):
        with open(project_path_name, 'w') as json_file:
            json.dump(self.data, json_file)
        
    def addLabel(self, text_label, img_name, landmark_coords_list=None):
        # Create unique label ID for all labels
        
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y/%H:%M:%S")
        label_id = 'label_' + dt_string
        
        if self.data['label_type'] == 'Text label':
            label_dict = {'label': text_label, 'label_id': label_id}
        elif self.data['label_type'] == 'Landmark label':
            label_dict = {'label_id': label_id, 'label': text_label, 'coords': landmark_coords_list[-1]}  
        elif self.data['label_type'] == 'Mask label':
            label_dict = {'label': text_label, 'label_id': label_id, 'coords': landmark_coords_list}
        
        self.data['images'][img_name]['labels'].append(label_dict)
                
    def removeImage(self, img_key):
        del self.data['images'][img_key]
        self.data['img_list_ordered'] = sorted(self.getImageList())
        
                
        if self.data['img_counter'] >= len(self.data['img_list_ordered']):
            self.data['img_counter'] = 0     

        
        
        
 
