# External libraries
import numpy as np
from PIL import Image
import json
from matplotlib.path import Path
  
def exportMaskDatasetAsNumpyArray(directory_path, project_data, training_test_ratio=0.9):
    # This function saves dictionary partition training/validation and 
    # dictionary label as local json file in directory_path. Masks are saved as numpy arrays.
    # Additionally the labeled images are transformed to grayscale/rgb and saved in directory_path.  
    partition_dict = {'train': [], 'validation': []}
    labels_dict = {}
    directory_img_source = project_data.data['folder_directory']
    
    # Only export images that were fully labeled
    min_labels = len(project_data.data['predefined_labels'])
    total_number_labeled_images = len(project_data.getImageList(min_labels))
    print('Total number labeled images: ', total_number_labeled_images)
    counter = 0

    #for img_key in project_data.data['images']:
    for img_key in project_data.data['img_list_ordered']:
        if len(project_data.data['images'][img_key]['labels']) >= min_labels:  
            counter = counter + 1
            sample_ID = 'ID' + str(counter) + '.png'
            
            img = Image.open(directory_img_source + "/" + img_key).convert('L')
            img.save(directory_path +'/' + sample_ID)
            img = np.array(img)
            
            if float(counter) / float(total_number_labeled_images) < training_test_ratio:
                partition_dict['train'].append(sample_ID)
                
            else:
                partition_dict['validation'].append(sample_ID)
                
            
            
            list_all_masks = []
            for index, label in enumerate(project_data.data['images'][img_key]['labels'], start=1):
                    ## Mask = value 1 for every pixel inside the mask contour, value 0 for every pixel outside
                    # Coords in (x,y) format
                    coords  =label['coords']
                        
                    # Adjust y axis direction
                    tupVerts = [[ coord[0], img.shape[0] - coord[1]] for coord in coords]
                    
                    x, y = np.meshgrid(np.arange(img.shape[1]), np.arange(img.shape[0])) # make a canvas with coordinates
                    x, y = x.flatten(), y.flatten()
                    points = np.vstack((x,y)).T 
                    
                    p = Path(tupVerts) # make a polygon
                    grid = p.contains_points(points)
                    mask = grid.reshape(img.shape[0],img.shape[1])
                    mask = np.expand_dims(mask, 2)
                    list_all_masks.append(mask)
                    
            # Convert list into numpy array
            numpy_array_all_masks = np.concatenate(list_all_masks, axis=2)
            
            # Create unique maskID
            maskID = 'ID' + str(counter) + '_label'
            labels_dict[sample_ID] = maskID
            
            # Note: there might be more memory efficient ways to save numpy arrays
            np.save(directory_path + '/' + maskID, numpy_array_all_masks)
            
    with open(directory_path + '/partition', 'w') as json_file:
        json.dump(partition_dict, json_file)
        
    with open(directory_path + '/labels', 'w') as json_file:
        json.dump(labels_dict, json_file)

def exportTextLabelDataset(directory_path, project_data, training_test_ratio=0.9):
    # This function saves dictionary partition training/validation and 
    # dictionary label as local json file in directory_path. 
    # Additionally the labeled images are transformed to grayscale/rgb and saved in directory_path.  
        
    partition_dict = {'train': [], 'validation': []}
    labels_dict = {}
    directory_img_source = project_data.data['folder_directory']
    
    total_number_labeled_images = len(project_data.getImageList(1))
    print('Total number labeled images: ', total_number_labeled_images)
    counter = 0

    for img_key in project_data.data['images']:
        if len(project_data.data['images'][img_key]['labels']) >= 1:  
            counter = counter + 1
            sample_ID = 'ID' + str(counter) + '.png'
            
            # For radiographs it is sufficient to convert images to grayscale, consider .convert('RGB') 
            # when using colored samples
            img = Image.open(directory_img_source + "/" + img_key).convert('L')
            img.save(directory_path +'/' + sample_ID)
            img = np.array(img)
            
            if float(counter) / float(total_number_labeled_images) < training_test_ratio:
                partition_dict['train'].append(sample_ID)
            else:
                partition_dict['validation'].append(sample_ID)
                
            # Save text label as list of indices
            labels = []
            for label_dict in project_data.data['images'][img_key]['labels']:
                index = project_data.data['predefined_labels'].index(label_dict['label'])
                labels.append(index)
            labels_dict[sample_ID] = labels

    with open(directory_path + '/partition', 'w') as json_file:
        json.dump(partition_dict, json_file)
        
    with open(directory_path + '/labels', 'w') as json_file:
        json.dump(labels_dict, json_file)
    
def exportLandmarkDataset(directory_path, project_data, training_test_ratio=0.9):
    # This function saves dictionary partition training/validation and 
    # dictionary label as local json file in directory_path. 
    # Additionally the labeled images are transformed to grayscale/rgb and saved in directory_path.  
        
    partition_dict = {'train': [], 'validation': []}
    labels_dict =  {}
    directory_img_source = project_data.data['folder_directory']
    
    total_number_labeled_images = len(project_data.getImageList(1))
    print('Total number labeled images: ', total_number_labeled_images)
    counter = 0

    for img_key in project_data.data['images']:
        if len(project_data.data['images'][img_key]['labels']) >= 1:  
            counter = counter + 1
            sample_ID = 'ID' + str(counter) + '.png'
            
            # For radiographs it is sufficient to convert images to grayscale, consider .convert('RGB') 
            # when using colored samples
            img = Image.open(directory_img_source + "/" + img_key).convert('L')
            img.save(directory_path +'/' + sample_ID)
            img = np.array(img)
            
            if float(counter) / float(total_number_labeled_images) < training_test_ratio:
                partition_dict['train'].append(sample_ID)
            else:
                partition_dict['validation'].append(sample_ID)
                
            # Save text label as list of indices
            labels = []
            for label_dict in project_data.data['images'][img_key]['labels']:
                label_dict['label'] = project_data.data['predefined_labels'].index(label_dict['label'])
                labels.append(label_dict)
            labels_dict[sample_ID] = labels

            
    with open(directory_path + '/partition', 'w') as json_file:
        json.dump(partition_dict, json_file)
        
    with open(directory_path + '/labels', 'w') as json_file:
        json.dump(labels_dict, json_file)


def exportMaskDataset(directory_path, project_data, training_test_ratio=0.9):
    # Old function, masks can be saved more memory efficient when saving each mask as png. 
    final_dict = {'partition': {'train': [], 'validation': []},  'list_IDs_img_masks': {}}
    for label in project_data.data['predefined_labels']:
        final_dict['labels_dict_' + label] = {}
    
    total_number_labeled_images = len(project_data.getImageList(7))
    print('Total number labeled images: ', total_number_labeled_images)
    counter = 0

    for img_key in project_data.data['images']:
        if len(project_data.data['images'][img_key]['labels']) > 6:  # Only images with all carpal  bones labeled
            counter = counter + 1
            label_ID = 'ID' + str(counter) + '.png'
            label_ID_path = directory_path + '/' + label_ID
            if project_data.data['color_mode'] == "RGB":
                img = Image.open(img_key).convert('RGB')
            else:
                img = Image.open(img_key).convert('L')
            img.save(label_ID_path)
            img = np.array(img)
            
            if float(counter) / float(total_number_labeled_images) < training_test_ratio:
                final_dict['partition']['train'].append(label_ID)
            else:
                final_dict['partition']['validation'].append(label_ID)
                print('val dict')
            
            #np_array_all_masks = 
            for index, label in enumerate(project_data.data['images'][img_key]['labels'], start=1):
                    #Create unique label ID
                    maskID = 'ID' + str(counter) +  '_label_' + label['label'] + '.png'
                    final_dict['labels_dict_' + label['label']][label_ID] = maskID
                    
                    # Coords in (x,y) format
                    coords  =label['coords']
                        
                    # Adjust y axis direction
                    coords = [[ coord[0], img.shape[0] - coord[1]] for coord in coords]
               
                    tupVerts = coords
                    
                    x, y = np.meshgrid(np.arange(img.shape[1]), np.arange(img.shape[0])) # make a canvas with coordinates
                    #x, y = np.meshgrid(np.arange(300), np.arange(300)) # make a canvas with coordinates
                    x, y = x.flatten(), y.flatten()
                    points = np.vstack((x,y)).T 
                    
                    p = Path(tupVerts) # make a polygon
                    grid = p.contains_points(points)
                    mask = grid.reshape(img.shape[0],img.shape[1])
                
                    mask = Image.fromarray(mask)
    
                    mask.save(directory_path + '/' + maskID)
                
            
    with open(directory_path + '/dict', 'w') as json_file:
        json.dump(final_dict, json_file)