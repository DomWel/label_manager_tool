import numpy as np
import vtkplotlib as vpl
from PyQt5 import QtCore, QtWidgets, QtGui

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

class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    """ This class is used as HTML delegate in the image label list. This way a colored box can 
    be placed next to the label. """
    def __init__(self, parent=None):
        super(HTMLDelegate, self).__init__(parent)
        self.doc = QtGui.QTextDocument(self)

    def paint(self, painter, option, index):
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        self.doc.setHtml(options.text)
        options.text = ""
        style = QtWidgets.QApplication.style() if options.widget is None \
            else options.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        if option.state & QtWidgets.QStyle.State_Selected:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.Text))
        textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, options, None)
        if index.column() != 0:
            textRect.adjust(5, 0, 0, 0)
        constant = 4
        margin = (option.rect.height() - options.fontMetrics.height()) // 2
        margin = margin - constant
        textRect.setTop(textRect.top() + margin)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(self.doc.idealWidth(), self.doc.size().height())  