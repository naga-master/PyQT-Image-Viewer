from PyQt5.QtCore import QPoint, pyqtSignal
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import QPoint, QRectF, QSize, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor,  QPainter, QPixmap
from PyQt5.QtWidgets import QFrame, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView,QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from pathlib import Path
from os import listdir
from os.path import join,  isfile
from themes import themes



class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.setFrameShape(QFrame.NoFrame)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAlignment(Qt.AlignCenter)
        self._photo.setTransformationMode(Qt.SmoothTransformation | QPainter.Antialiasing)
        
        
    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                self._find_factor(rect)
            self._zoom = 0

    def _find_factor(self, rect):
        unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        viewrect = self.viewport().rect()
        scenerect = self.transform().mapRect(rect)
        factor = min(viewrect.width() / scenerect.width(),
                     viewrect.height() / scenerect.height())

        if factor <= 1:  #restrict scale the small images 
            self.scale(factor, factor)

        if rect.width() > 400 and factor < 0.04:
            #came here because viewrect gives wrong value
            print('View Rect Wrong Value')
            self.scale(factor, factor)
            QTimer.singleShot(0, self.fitInView) # Don't modify this line

    

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)


class ThumbnailWidget (QWidget):

    def __init__ (self, parent = None):
        super(ThumbnailWidget, self).__init__(parent)
        self.thumbnailQVBoxLayout = QVBoxLayout()
        self.thumbnail_file_name_label = QLabel()
        self.thumbnail_image_label = QLabel()

        self.thumbnail_file_name_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_image_label.setAlignment(Qt.AlignCenter)
        self.thumbnailQVBoxLayout.setAlignment(Qt.AlignCenter)
        
        self.thumbnail_file_name_label.setWordWrap(True)
        self.font_metrics = self.thumbnail_file_name_label.fontMetrics()
          
        self.thumbnail_file_name_label.setStyleSheet(
           themes.THUMBNAIL_WIDGET_THEME
        )
        
        self.setLayout(self.thumbnailQVBoxLayout)
        
    
    def setTextUp (self, filename):
        self.thumbnailQVBoxLayout.addWidget(self.thumbnail_file_name_label)
        self.elided_text = self.font_metrics.elidedText(filename, Qt.ElideRight, 100)
        self.thumbnail_image_label.setToolTip(filename)
        self.thumbnail_image_label.setToolTipDuration(5000)
        self.thumbnail_file_name_label.setText(self.elided_text)
        

    def setImage(self, path):
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(
            QSize(100,100),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.thumbnail_image_label.setPixmap(pixmap)
        self.thumbnailQVBoxLayout.addWidget(self.thumbnail_image_label) 


class ImageWidget(QWidget):
    def __init__(self, folder, parent=None):
        super(ImageWidget, self).__init__()
        
        self.items_dict = {}
        self.image_directory = folder

        self.VBlayout = QVBoxLayout(self)
        self.viewer = PhotoViewer(self)
        self.myQListWidget = QListWidget(self)

        self.VBlayout.addWidget(self.viewer) # add main image graphicsscene widget to layout
        self.VBlayout.setAlignment(Qt.AlignCenter)    

        self.myQListWidget.itemSelectionChanged.connect(self.itemselected) #signal definition for listwidget selection
        self.myQListWidget.setFixedHeight(200)
        self.myQListWidget.setFlow(0)
        self.myQListWidget.setFocusPolicy(Qt.NoFocus)
        
        self.setLayout(self.VBlayout)
        self.buildMainWidgets(self.image_directory)

    def getImagesFromDirectory(self, directory):
        for file in listdir(directory):
            if isfile(join(directory, file)) and self.filename_has_image_extension(file):
                yield file

        

    def buildMainWidgets(self, directory):
        self.items_dict.clear() #clear the dictionary

        files = self.getImagesFromDirectory(directory)
        
        for index, file in enumerate(sorted(files)):
            
            filepath =join(directory,file)

            myThumbnailWidget  = ThumbnailWidget() # Create ThumbnailWidget  
            myQListWidgetItem = QListWidgetItem(self.myQListWidget) # Create QListWidgetItem
            myThumbnailWidget.setImage(filepath)
            myThumbnailWidget.setTextUp(file)
                            
            # Set size hint
            myQListWidgetItem.setSizeHint(myThumbnailWidget.sizeHint())

            self.items_dict[index] = (myQListWidgetItem, filepath)
            # Add QListWidgetItem into QListWidget
            self.myQListWidget.addItem(myQListWidgetItem)
            self.myQListWidget.setItemWidget(myQListWidgetItem, myThumbnailWidget)
        

    def keyPressEvent(self, event):
        key_pressed = event.key()
        
        cur_selected_item = self.myQListWidget.currentItem()  #get current selected item
                
        if key_pressed in [Qt.Key_Up, Qt.Key_Right]:
            key=next(self.get_item_index(self.items_dict, cur_selected_item)) # find the selected item index
            cur_selected_index = key+1 #key[0] + 1     #increament the current to next index 
            if cur_selected_index == len(self.items_dict): cur_selected_index = 0 #reset the index to first when the last image reached
            self.myQListWidget.setCurrentItem(self.items_dict[cur_selected_index][0]) # set current index image
            

        elif key_pressed in [Qt.Key_Down, Qt.Key_Left]:
            key=next(self.get_item_index(self.items_dict, cur_selected_item)) # find the selected item index
            cur_selected_index =  key  #key[0] 
            if cur_selected_index == 0: cur_selected_index = len(self.items_dict) #reset the index to last when the first image selected
            self.myQListWidget.setCurrentItem(self.items_dict[cur_selected_index-1][0]) # set current index image
            

    def get_item_index(self, dict, item):
        for key, value in dict.items():
            if value[0] ==  item:
                yield key
        

    def itemselected(self):
        cur_selected_item = self.myQListWidget.selectedItems()
        key=next(self.get_item_index(self.items_dict, cur_selected_item[0])) # find the selected item index
        #if len(key) > 1: print('multiple items returned')
        self.viewer.setPhoto(QPixmap(self.items_dict[key][1]))   

    ## Check that a file name has a valid image extension for QPixmap
    def filename_has_image_extension(self, filename):
        valid_img_extensions = \
            ['.bmp', '.gif', '.jpg', '.jpeg', '.png', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm']
        extension= Path(filename.lower()).suffix
        return extension in valid_img_extensions
