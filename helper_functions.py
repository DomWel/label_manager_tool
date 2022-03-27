import numpy as np
import vtkplotlib as vpl

def getLabelColor(predef_labels, color_list, label_name):
    index = predef_labels.index(label_name)
    return color_list[index]
        
def computeCamPos(img_orig, img_dims, img_spacing, viewing_angle):
    x_cp = img_orig[0] + 0.5 * img_dims[0] * img_spacing[0]
    y_cp = img_orig[1] + 0.5 * img_dims[1] * img_spacing[1]
    max_length = max(x_cp, y_cp)
    z_cp = max_length / np.tan( viewing_angle / 360.0 * np.pi)
    return [x_cp, y_cp, z_cp]
    
def getEmptyImage():
    empty_img_np = np.zeros((50, 50), dtype=np.uint8)
    vtk_image = vpl.image_io.as_vtkimagedata(empty_img_np, ndim=None)
    return vtk_image