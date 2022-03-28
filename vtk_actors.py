import vtk
from helper_functions import getLabelColor

def createPointsPolydata(landmark_pos):
    points = vtk.vtkPoints()
    for pos in landmark_pos:
        points.InsertNextPoint(pos[0], pos[1], 0)
    polydata_points = vtk.vtkPolyData()
    polydata_points.SetPoints(points)
    return polydata_points

def createCaptionActors(number, font_size, color=[1,0,0], visibility=False, start_pos=[0,0,0]):
    caption_actors = []
    for i in range(number):
        captionActor = vtk.vtkCaptionActor2D()
        captionActor.SetCaption('')
        captionActor.SetAttachmentPoint(start_pos)
        captionActor.BorderOff()
        captionActor.GetCaptionTextProperty().BoldOff()
        captionActor.GetCaptionTextProperty().ItalicOff()
        captionActor.GetTextActor().SetTextScaleModeToNone()
        captionActor.GetCaptionTextProperty().SetFontSize(font_size)
        captionActor.GetCaptionTextProperty().SetColor(color)
        captionActor.ThreeDimensionalLeaderOff()
        captionActor.SetVisibility(visibility)
        caption_actors.append(captionActor)
    return caption_actors

def createLinesPolydata(landmark_pos, last_line=False, ext_mask_points=None):
    # Create a vtkPoints object and store the points in it
    points = vtk.vtkPoints()
    if ext_mask_points != None:
        list_points = ext_mask_points
    else:
        list_points = landmark_pos
    for pos in list_points:
        points.InsertNextPoint(pos[0], pos[1], 0)
    landmarks_count = len(list_points)
    if last_line:
        points.InsertNextPoint(list_points[0][0], list_points[0][1], 0)
        landmarks_count = landmarks_count+1
    polyLine = vtk.vtkPolyLine()
    polyLine.GetPointIds().SetNumberOfIds(landmarks_count)
    for i in range(landmarks_count):
        polyLine.GetPointIds().SetId(i, i)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyLine)
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(points)
    polyData.SetLines(cells)
    return polyData

def deleteLastPoint(points):
    newPoints = vtk.vtkPoints()
    number_points = points.GetNumberOfPoints() 
    if number_points > 0:
        for i in range(points.GetNumberOfPoints() - 1):
            p = points.GetPoint(i)
            newPoints.InsertNextPoint(p)
    return newPoints

def createMaskLabelActors(label_list, landmark_pos, predef_labels, color_list ):
    lineMappers = []
    lineActors = []
    for i, label in enumerate(label_list, start=0): 
        lineMappers.append(vtk.vtkPolyDataMapper())
        polyDataLines = createLinesPolydata(landmark_pos, last_line=True, ext_mask_points=label['coords'])
        lineMappers[i].SetInputData(polyDataLines)
        lineActors.append( vtk.vtkActor() )
        lineActors[i].SetMapper(lineMappers[i])
        color_rgb = getLabelColor(predef_labels, color_list, label['label'])
        lineActors[i].GetProperty().SetColor(color_rgb)
        lineActors[i].SetVisibility(True)
    return lineActors
        
def createCurrentActorLines(visibility=True):      
    mapper_lines = vtk.vtkPolyDataMapper()
    current_line_actor = vtk.vtkActor()
    current_line_actor.SetMapper(mapper_lines)
    current_line_actor.SetVisibility(visibility)
    return current_line_actor
    
def createGlyphActor(visibility=True, radius=1, number_of_sides=200):
    points = vtk.vtkPoints()
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polygonSourceGlyph = vtk.vtkRegularPolygonSource()  
    polygonSourceGlyph.SetRadius(radius)
    polygonSourceGlyph.SetNumberOfSides(number_of_sides)
    glyph2D = vtk.vtkGlyph2D()
    glyph2D.SetSourceConnection(polygonSourceGlyph.GetOutputPort())
    glyph2D.SetInputData(polydata)
    glyph2D.Update()
    mapper_glyph = vtk.vtkPolyDataMapper()
    mapper_glyph.SetInputConnection(glyph2D.GetOutputPort())
    mapper_glyph.Update()
    current_glyph_actor = vtk.vtkActor()
    current_glyph_actor.SetMapper(mapper_glyph)
    return current_glyph_actor, glyph2D


def addCurrentMaskLabelActors(self):
    # Current mask label =  Caption actor + Glyph actor + Lines Actor!
    if len(self.landmark_pos) > 0: 
        label_combobox = self.combobox_label_selection.currentText()
        color_rgb = getLabelColor(self.project_data.data['predefined_labels'], 
                                  self.project_data.data['color_list'], 
                                  label_combobox)
        
        self.ren.RemoveActor(self.captionActor)
        self.captionActor.SetCaption('New label: ' + label_combobox)
        self.captionActor.GetCaptionTextProperty().SetColor(color_rgb)
        self.captionActor.SetVisibility(True)
        self.captionActor.SetAttachmentPoint(self.landmark_pos[0][0], self.landmark_pos[0][1], 0)
        self.ren.AddActor(self.captionActor)
        
        # Load line actor with new data
        polyDataLines = createLinesPolydata(self.landmark_pos)
        self.mapper_lines.SetInputData(polyDataLines)
        
        # Load glyph2d actors with new data
        polydata_labels = createPointsPolydata(self.landmark_pos)
        self.glyph2D.SetInputData(polydata_labels)
        
        # Adjust color and make actors visible
        self.current_line_actor.GetProperty().SetColor(color_rgb)
        self.current_line_actor.SetVisibility(True)
        self.ren.AddActor(self.current_line_actor)
        
        self.current_glyph_actor.GetProperty().SetColor(color_rgb)
        self.current_glyph_actor.SetVisibility(True)
        self.ren.AddActor(self.current_glyph_actor)

def addCurrentLandmarkActor(self):
    # Current landmark acotr = Caption actor
    if len(self.landmark_pos) > 0: 
        label_combobox = self.combobox_label_selection.currentText()
        color_rgb = getLabelColor(self.project_data.data['predefined_labels'], 
                                  self.project_data.data['color_list'], 
                                  label_combobox)
        
        if self.project_data.data['label_type'] == 'Landmark label':
            self.captionActor.SetCaption('New label: ' + label_combobox)
            self.captionActor.SetAttachmentPoint(self.landmark_pos[-1][0], self.landmark_pos[-1][1], 0)
            self.captionActor.SetVisibility(True)
            self.captionActor.GetCaptionTextProperty().SetColor(color_rgb)
            self.ren.AddActor(self.captionActor)