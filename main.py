# External libraries
import sys
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
import vtk
# Project files
import interface
from data_class import project_data
import vtk_actors 
from helper_functions import getLabelColor

class MainWindow(Qt.QMainWindow):
    def __init__(self, parent = None):
        Qt.QMainWindow.__init__(self, parent) 
        
        # Adjust window size        
        self.resize(1400, 900)    
        
        #Create Project Database
        self.project_data = project_data()

        # Create VTK render window
        self.renderWindow = vtk.vtkImageViewer2()
        self.ren = self.renderWindow.GetRenderer()
      
        # Create QT display interfaces that show VTK pipeline output             
        self.frame = Qt.QFrame()      
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)  
        self.setCentralWidget(self.frame)
        
        #Create interactor style
        ## Modified version of vtk Interactor style image
        style = MyInteractorStyle(parent=self)
        
        # Setup of QT GUI
        interface.initUI(self)
        
        # Connect VTK pipeline renderer to QT frame display 
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)    
        
        # Set main window visible and access render window interactor
        self.show()
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.SetInteractorStyle(style)

    # Subwindows
    def newProject(self):
        self.new_proj_diag = NewProjectDialogue(parent=self)
        self.new_proj_diag.show()
        
    def editPredefLabels(self):
        self.edit_predef_labels = PredefinedLabelsMenu(parent=self)
        self.edit_predef_labels.show()
        
    def loadProjectMenu(self):
        self.load_project_menu = LoadProjectMenu(parent=self)
        self.load_project_menu.show()

class MyInteractorStyle(vtk.vtkInteractorStyleImage):

    def __init__(self, parent=None):
        self.AddObserver('LeftButtonPressEvent', self.left_button_press_event)
        self.AddObserver('RightButtonPressEvent', self.right_button_press_event)
        self.parent = parent

    def left_button_press_event(self, obj, event):
        # Image only interactable if landmark/mask label is set and a label is selected via the combobox
        if (self.parent.project_data.data['label_type'] == 'Landmark label' or\
            self.parent.project_data.data['label_type'] == 'Mask label' ) and \
            self.parent.combobox_label_selection.currentText() != "":
            
            # Get position of mouse in world coordinates
            x = self.parent.iren.GetEventPosition()[0]
            y = self.parent.iren.GetEventPosition()[1]
            picker = vtk.vtkPropPicker()
            picker.Pick(x, y, 0, self.parent.ren)
            pickerWorld = picker.GetPickPosition()
            self.parent.landmark_pos.append([pickerWorld[0], pickerWorld[1]])
            
            if self.parent.project_data.data['label_type'] == 'Landmark label':
                vtk_actors.addCurrentLandmarkActor(self.parent)
                
            elif self.parent.project_data.data['label_type'] == 'Mask label':
                vtk_actors.addCurrentMaskLabelActors(self.parent)

            self.parent.iren.Initialize()
            self.parent.iren.Start()    
            
            self.OnLeftButtonDown () 
        return
    
    def right_button_press_event(self, obj, event):
        if self.parent.project_data.data["label_type"] == "Mask label":
            idx = len(self.parent.landmark_pos)
            self.parent.landmark_pos = self.parent.landmark_pos[:-1]
            
            if idx > 0:
                if idx == 1: 
                    self.parent.ren.RemoveActor(self.parent.captionActor)

                new_polydata_labels = vtk_actors.createPointsPolydata(self.parent.landmark_pos)
                self.parent.glyph2D.SetInputData(new_polydata_labels)
                
                polyDataLines = vtk_actors.createLinesPolydata(self.parent.landmark_pos)
                self.parent.mapper_lines.SetInputData(polyDataLines)
                
            self.parent.iren.Initialize()
            self.parent.iren.Start()    
        
        self.OnRightButtonDown () 
        return

class NewProjectDialogue(Qt.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.new_proj_flag = False
        interface.initNewProjDiag(self)  
        layout = self.new_proj_grid
        self.setLayout(layout)
 
class PredefinedLabelsMenu(Qt.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.new_proj_flag = False
        interface.initPredefinedLabelsEditMenu(self)  
        layout = self.predefined_labels_edit_menu
        self.setLayout(layout)
        
    def changePreselectLabelName(self):
        self.change_preselect_label_name = ChangePreselctLabelName(parent=self)
        self.change_preselect_label_name.show()

class LoadProjectMenu(Qt.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.new_proj_flag = False
        interface.initLoadProjectMenu(self)  
        layout = self.load_project_menu
        self.setLayout(layout)
        
class ChangePreselctLabelName(Qt.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        interface.initChangePreselectLabelName(self)  
        layout = self.change_label_name_grid
        self.setLayout(layout)

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())