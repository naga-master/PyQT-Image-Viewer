THUMBNAIL_WIDGET_THEME =  '''
            color : #FFFFFF;
            '''

FOLDER_DIALOG_THEME = '''
        QWidget{
            background-color: #34373c;
            color: #FFFFFF;
            border: 2px solid #40454b;
            border-radius: 10px;
            padding: 6px;
        }

        QPushButton:hover {
            background-color: #389bd9;
        }

        QLineEdit:focus {
            border: 2px solid #389bd9;
            border-radius: 10px;
        }
        
        '''

MAINWINDOW_THEME = '''
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

        QScrollBar::handle:horizontal:hover,QScrollBar::handle:horizontal:pressed {
            background-color: #6a6ea9;

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
