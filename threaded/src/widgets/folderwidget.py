from PyQt5.QtWidgets import QDesktopWidget, QFileDialog, QWidget, QGridLayout, QHBoxLayout, QLineEdit, QPushButton
from themes import themes
from os.path import isdir

class FolderDialog(QWidget):

    def __init__(self):
        super(FolderDialog, self).__init__()
        #self.setGeometry(300,300,300,300)
        self.folderWidget()
        
        
    def folderWidget(self):
        widget_frame = QGridLayout()
        folder_layout = QHBoxLayout()
        ok_cancel_layout = QHBoxLayout()
        self.folder_entry =  QLineEdit(
            objectName = 'folderentry'
        )
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
        self.authenticate = False

        self.folder_entry.setPlaceholderText('Choose Directory')
        self.folder_entry.textChanged.connect(lambda:self.on_text_change())
        
        self.setFixedWidth(400)
        self.setFixedHeight(150)
        self.setStyleSheet(themes.FOLDER_DIALOG_THEME)
   

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

    def center(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def open_directory(self):
        self.folder_path =  QFileDialog.getExistingDirectory(self,'Choose Directory')
        self.folder_entry.setText(self.folder_path)

    def on_ok(self):
        self.folder_path=self.folder_entry.text()
        

        
    def on_text_change(self):
        self.folder_path=self.folder_entry.text()
        if not isdir(self.folder_path):
            self.folder_entry.setStyleSheet(
                '''
                #folderentry{
                    
                    border : 2px solid red;
                    border-radius : 10px;
                }
                '''
            )
            
            #print('selected folder is not valid')
            self.authenticate = False
        else:
            #print('valid folder')
            self.folder_entry.setStyleSheet(
                '''
                #folderentry{
                    
                    border : 2px solid #389bd9;
                    border-radius : 10px;
                }
                '''
            )            
            self.authenticate = True
