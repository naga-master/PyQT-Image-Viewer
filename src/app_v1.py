import sys, os, pathlib, json
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QRectF, QSize, QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QColor,  QKeySequence, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QFileDialog,  QFrame, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGridLayout, QHBoxLayout,  QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMenuBar, QPushButton, QSizePolicy,  QStatusBar, QVBoxLayout, QWidget



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
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())

                if not factor > 1:  #restrict scale the small images 
                    self.scale(factor, factor)

                if rect.width() > 400 and factor < 0.04:
                    #came here because viewrect gives wrong value
                    print('View Rect Wrong Value')
                    self.scale(factor, factor)
                    QTimer.singleShot(0, self.fitInView)
                

            self._zoom = 0

    

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
            #self.resize(pixmap.width(), pixmap.height())
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
            '''
            color : #FFFFFF;
            '''
        )
        
        self.setLayout(self.thumbnailQVBoxLayout)
        
    
    def setTextUp (self, filename):
        self.thumbnailQVBoxLayout.addWidget(self.thumbnail_file_name_label)
        self.elided_text = self.font_metrics.elidedText(filename, Qt.ElideRight, 100)
        self.thumbnail_image_label.setToolTip(filename)
        self.thumbnail_image_label.setToolTipDuration(10000)
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
        
        self.items_dict ={}
        self.image_directory = folder
        print(self.image_directory)

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

        

    def buildMainWidgets(self, directory):
        self.items_dict ={}

        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and self.filename_has_image_extension(f)]
   
        for index, file in enumerate(sorted(files)):
            #print(file)
            
            filepath =os.path.join(directory,file)

            myThumbnailWidget = ThumbnailWidget() # Create ThumbnailWidget
            myQListWidgetItem = QListWidgetItem(self.myQListWidget) # Create QListWidgetItem
            
            myThumbnailWidget.setImage(filepath)
            myThumbnailWidget.setTextUp(file)
            
                        
            # Set size hint
            myQListWidgetItem.setSizeHint(myThumbnailWidget.sizeHint())

            self.items_dict[index] = [myQListWidgetItem, filepath]
            # Add QListWidgetItem into QListWidget
            self.myQListWidget.addItem(myQListWidgetItem)
            self.myQListWidget.setItemWidget(myQListWidgetItem, 
                                myThumbnailWidget)

    def keyPressEvent(self, event):
        key_pressed = event.key()
        
        cur_selected_item = self.myQListWidget.currentItem()  #get current selected item
        keys=self.get_item_index(self.items_dict, cur_selected_item) # find the selected item index
        if len(keys) > 1: print('multiple items returned')
        
        if key_pressed in [Qt.Key_Up, Qt.Key_Right]:
            
            cur_selected_index = keys[0] + 1     #increament the current to next index 
            if cur_selected_index == len(self.items_dict): cur_selected_index = 0 #reset the index to first when the last image reached
            self.myQListWidget.setCurrentItem(self.items_dict[cur_selected_index][0]) # set current index image
            #print('Up or Right Arrow Pressed')

        elif key_pressed in [Qt.Key_Down, Qt.Key_Left]:

            cur_selected_index =  keys[0] 
            if cur_selected_index == 0: cur_selected_index = len(self.items_dict) #reset the index to last when the first image selected
            self.myQListWidget.setCurrentItem(self.items_dict[cur_selected_index-1][0]) # set current index image
            #print('Down or Left Arrow Pressed')

    def get_item_index(self, dict, item):
        keys = [key for key, value in dict.items() if value[0] == item]
        return keys

    def itemselected(self):
        cur_selected_item = self.myQListWidget.selectedItems()
        keys=self.get_item_index(self.items_dict, cur_selected_item[0]) # find the selected item index
        if len(keys) > 1: print('multiple items returned')
        self.viewer.setPhoto(QPixmap(self.items_dict[keys[0]][1]))   

    ## Check that a file name has a valid image extension for QPixmap
    def filename_has_image_extension(self, filename):
        valid_img_extensions = \
            ['.bmp', '.gif', '.jpg', '.jpeg', '.png', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm']
        filename = filename.lower()
        extension= pathlib.Path(filename).suffix
        if not extension in valid_img_extensions :
            return False

        return True

    

class FolderDialog(QWidget):


    def __init__(self):
        super(FolderDialog, self).__init__()
        #self.setGeometry(300,300,300,300)
        self.folderWidget()
        
        
    def folderWidget(self):
        widget_frame = QGridLayout()
        folder_layout = QHBoxLayout()
        ok_cancel_layout = QHBoxLayout()
        self.folder_entry =  QLineEdit()
        browse_button = QPushButton(
            'Browse',
            clicked = self.open_directory)
        self.ok_button = QPushButton(
            'Ok',
            clicked = self.on_ok
        )
        cancel_button = QPushButton(
            'Cancel',
            clicked = self.close
        )

        self.folder_entry.setPlaceholderText('Choose Directory')
   

        widget_frame.setHorizontalSpacing(10)
        widget_frame.setVerticalSpacing(10)
        widget_frame.setContentsMargins(20,20,20,20)
        widget_frame.setColumnStretch(1,1)
        

        ok_cancel_layout.addWidget(self.ok_button)
        ok_cancel_layout.addWidget(cancel_button)

        folder_layout.addWidget(self.folder_entry)
        folder_layout.addWidget(browse_button)

        
        widget_frame.addLayout(folder_layout,0,0,1,2)
        widget_frame.addLayout(ok_cancel_layout,1,0,1,2)

        self.setLayout(widget_frame)
        
        self.center()
        #self.show()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def open_directory(self):
        self.folder_path =  QFileDialog.getExistingDirectory(self,'Choose Directory')
        #print(self.folder_path)
        self.folder_entry.setText(self.folder_path)

    def on_ok(self):
        self.folder_path=self.folder_entry.text()
        #print(self.folder_path)



class MainWindow(QMainWindow):
    def __init__(self, foldername,parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('app')
        self.folder = foldername
        self._createMenu()
        self._setlayout()
        self._createStatusBar()
        screen = QDesktopWidget().availableGeometry()
        self.setGeometry(0,0,screen.width(),screen.height())
        self.setMinimumSize(QSize(500,500))
        self.setStyleSheet(stylesheet)
                
    def _createMenu(self):
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu('File')
        self.open_act =  file_menu.addAction('Open')
        file_menu.addSeparator()
        quit_act = file_menu.addAction('Quit', self.close)

        self.open_act.setShortcut(QKeySequence.Open)
        quit_act.setShortcut(QKeySequence.Quit)
        

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage('Welcome to Image Viewer', 5000)
        self.setStatusBar(status)

    def _setlayout(self):
        widget = QWidget()
        self.image_layout = QGridLayout()
        self._addImageWidget()
        widget.setLayout(self.image_layout)
        self.setCentralWidget(widget)

    def _addImageWidget(self):
        self.image_viewer = ImageWidget(self.folder)
        self.image_layout.addWidget(self.image_viewer,1,0)
        self.image_layout.addWidget(self.image_viewer.myQListWidget,2,0)

        self.image_viewer.myQListWidget.setCurrentItem(self.image_viewer.items_dict[0][0]) #set current index to zero
        image = QPixmap(self.image_viewer.items_dict[0][1])
        self.image_viewer.viewer.setPhoto(image) #display first image 

    def keyPressEvent(self, event):
        self.image_viewer.keyPressEvent(event)

        

stylesheet='''
        QMenuBar {
            background-color: #34373c;
            border: 1px solid #000;
        }
        QMenuBar::item {
            color: #FFFFFF;
        }

        QMenuBar::item::selected {
            background-color: #40454b;
        }

        QMenu , QStatusBar, QMainWindow{
            background-color:  #34373c;
            color: #FFFFFF;
            border: 1px solid #000;           
        }
        

        QMenu::item::selected {
            background-color: #40454b;
        }

        QListWidget {
         background-color:  #34373c;   
        }
        QListView::item:selected {
            border: 2px solid #6a6ea9;
            border-radius: 15px;
            color: white;
        }

        QToolTip{
            background-color: #34373c; 
            color: white; 
            border: 2px solid #6a6ea9;
            border-radius: 7px;
        }

        QScrollBar:horizontal, QScrollBar:vertical {              
            border: none;
            background:#34373c;
            height:10px;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop: 0 rgb(64, 69, 75), stop: 0.5 rgb(64, 69, 75), stop:1 rgb(64, 69, 75));
            min-height: 0px;
            border-radius: 5px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::add-line:veritcal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop: 0 rgb(64, 69, 75), stop: 0.5 rrgb(64, 69, 75),  stop:1 rgb(64, 69, 75));
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
            border-radius: 5px;
        }
        QScrollBar::sub-line:horizontal, QScrollBar::sub-line:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop: 0  rgb(64, 69, 75), stop: 0.5 rgb(64, 69, 75),  stop:1 rgb(64, 69, 75));
            height: 0 px;
            subcontrol-position: top;
            subcontrol-origin: margin;
            border-radius: 5px;
        }
        
         QGraphicsView {
            border : 5px solid black;
            border-radius: 10px;
        }
        '''


class MainApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.folder_window =  FolderDialog()
        
        self.folder_window.ok_button.clicked.connect(self.openMainWindow)
        self.folder_window.ok_button.clicked.connect(self.folder_window.close)

        self.folder_window.show()

    def openMainWindow(self):
        self.main_window = MainWindow(self.folder_window.folder_path)
        self.main_window.open_act.triggered.connect(self.closeMainWindow)
        self.main_window.open_act.triggered.connect(self.folder_window.show)
        self.main_window.show()

    def closeMainWindow(self):
        self.main_window.close()
        self.folder_window.folder_entry.clear()








if __name__ =="__main__":
    
    app = MainApp(sys.argv)
    sys.exit(app.exec_())
