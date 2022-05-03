from PyQt5 import Qt
import interface

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