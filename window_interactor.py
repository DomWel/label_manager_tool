import vtk
import vtk_actors


class InteractorStyle(vtk.vtkInteractorStyleImage):

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