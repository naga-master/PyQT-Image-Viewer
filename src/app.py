import sys, os, pathlib, json
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QRectF, QSize, QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QColor,  QKeySequence, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QFileDialog,  QFrame, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGridLayout, QHBoxLayout,  QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMenuBar, QPushButton, QSizePolicy,  QStatusBar, QVBoxLayout, QWidget
from widgets.folderwidget import FolderDialog
from widgets.imageviewer import ImageWidget
from themes import themes

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
        self.setStyleSheet(themes.MAINWINDOW_THEME)
                
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



class MainApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.showFolderWindow()
        

    def showFolderWindow(self):
        self.folder_window =  FolderDialog()  #load folder widget
        
        self.folder_window.ok_button.clicked.connect(self.showMainWindow)
        self.folder_window.ok_button.clicked.connect(self.folder_window.close)
        
        self.folder_window.show()

    def showMainWindow(self):
        if self.folder_window.authenticate:
            self.main_window = MainWindow(self.folder_window.folder_path) #load main widget
            self.main_window.open_act.triggered.connect(self.closeMainWindow)
            self.main_window.open_act.triggered.connect(self.folder_window.show)
            self.main_window.show()
        else :
            
            self.showFolderWindow()

    def closeMainWindow(self):
        #self.main_window.close() 
        self.folder_window.folder_entry.clear()


if __name__ =="__main__":
    
    app = MainApp(sys.argv)
    sys.exit(app.exec_())

