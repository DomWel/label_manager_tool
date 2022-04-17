# Label manager tool
PyQT and VTK-based GUI for text, landmark and mask labeling of image data.

## Requirements an program start
The provided code has been tested with Python 3.6.6 on macOS 11 Big Sur. The following Python packages are required (lower versions may also be sufficient):
- Matplotlib >= 3.0.3
- Numpy >= 1.13.0
- pyqt ==5.13 (PyQt > 5.13 seems to cause problems on macOS Big Sur when starting the Python script from terminal)
- VTK >= 8.1.0
- vtkplotlib>=1.5.1
- Pillow >= 8.4.0

Quickstart using Anaconda:
1) Create new environment
2) conda install pip
3) pip install -r requirements.txt
4) python main.py

##Start a new project
1) Press on "New project"
2) Choose a project name, label type, grayscale/rgb and create label classes
3) Complete the creation process by clicking on the "Create" button
4) Press on "Load image data" and select the directory of the image source
5) Start labeling!

## Labeling process
- Labels are added and removed by pressing the corresponding buttons
- During the labeling process it is possible to add new label classes and edit or remove existing label classes using the "Edit label class list" menu
- Landmark labels can be added by clicking on the desired position on the image and press the "Add landmark label" button
- Mask labels are defined piecewise by sequentially placing points to form the contour of the desired mask. Upon clicking "Add mask label" the last point will be connected to first point; right-clicking removes the last point of the contour points


## Image control panel
- All images of type JPEG or PNG localized in the specified directory or its subdirectories will be added to the project data and appear in the image list display and the project summary
- Images can be selected by pressing the "Backward" / "Forward" buttons or by directly clicking on the image name in the image list display or the project summary
- Images can be deleted by pressing "Remove image" (also removes the corresponding image labels)
- By clicking on "Update images" the directory will be searched for new images and the project data will be updated (already removed images will not be imported again)
- In unclear cases an image can be marked using the checkbox "Expert review needed". The image will appear in the project summary under "Expert review needed" and can be easily accessed from there
- Contrast / Brightness of grayscale images can be adjusted by moving the cursor along the horizontal / vertical image axis while holding down the left mouse button

## Save and export
- Preliminary results can be saved and loaded using the corresponding buttons
- During the loading process it is necessary to confirm the path to the image directory or correct it if necessary (this is the case if the project file is loaded from the local machine of another user and the path to the image directory has changed)
- Export function generates a folder containing the labeled images and two JSON files ("partition" and "labels") as recommended in https://stanford.edu/~shervine/blog/keras-how-to-generate-data-on-the-fly
- When labeling results are exchanged between two users, both have to use the same image source
- Don't change the directory structure within a image directory source or rename images!!
- Adding of additional files to the image directory is possible, press "Update image data" to update the project data and the UI image list
