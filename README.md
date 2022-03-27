# Label manager tool
PyQT and VTK-based GUI for text, landmark and mask labeling of image data.

## Requirements
The provided code has been tested with Python 3.6.6 on macOS 11 Big Sur. The following Python packages are required (lower versions may also be sufficient):
- Matplotlib >= 3.0.3
- Numpy >= 1.13.0
- pyqt >= 5.6.0
- VTK >= 8.1.0
- vtkplotlib>=1.5.1
- Pillow >= 8.4.0

Quickstart using Anaconda:
1) Create new environment
2) conda install pip
3) pip install -r requirements.txt

## Program start
1) Open your IDE (e.g. Spyder) and run the the main file (Note: the first start might take a few minutes)
2) Press "New project"
3) Choose a project name, label type, grayscale/rgb and create label classes
4) Press "Create"
5) Press "Load image data" and select the directory of the image source

## Labeling process
- Generally labels are added / removed by using the "Add label" / "Remove label" button; it's possible to label a sample with multiple labels
- During the labeling process it is possible to add new label classes and edit or remove existing label classes (Note: removing a label class will remove all associated image labels!!!!)
- Landmark labels can be added by clicking on the desired image position and press the "Add landmark label" button
- Mask labels are defined piecewise by sequentially placing multiple points along the desired contour of the mask, upon clicking "Add mask label" the last point will be connected to first point; right-clicking removes the last point of the contour points

## Image control panel
- All images of type .jpg or .png localized in the specified directory and its subdirectories will be added to the project data and appear in the image control display and the project summary
- Images can be selected by using the "Backward" / "Forward" buttons or by directly clicking on the image name in the image name display or the project summary
- Images can be deleted by pressing "Remove image" (also removes the corresponding image labels)
- By clicking on "Update images" the directory will be searched for new images and the  project data will be updated
- In unclear cases an image can be marked using the checkbox "Expert review needed"; those marked images will appear in project summary under "Expert review needed" and are easy accessible to others
- Contrast / Brightness of the image can be adjusted by moving the cursor along the horizontal / vertical image axis while holding down the left mouse button

## Save and export
- Preliminary results can be saved / loaded using the corresponding buttons
- During the loading process it is necessary to confirm the path to the image directory or correct it if necessary (this is the case if the project file is loaded from the computer of antoher user and the path to the image directory has changed)
- Export function generates a folder containing the labeled images and two JSON files ("partition" and "labels") as recommended in https://stanford.edu/~shervine/blog/keras-how-to-generate-data-on-the-fly
- When labeling results are exchanged between two users, both have to specify the same image directory path when loading the project
- Don't change the directory structure within a image directory source or rename images within the file!!
- Adding of addiotional files to the image directory is possible, press "Update image data" to update the project data and GUI image list
