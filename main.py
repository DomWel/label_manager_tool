# External libraries
import sys
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
#from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
import vtk
# Project files
import interface
from data_class import project_data
from subwindows import NewProjectDialogue, PredefinedLabelsMenu, LoadProjectMenu
from window_interactor import InteractorStyle

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
        style = InteractorStyle(parent=self)
        
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



if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())