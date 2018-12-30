import sys
from PySide import QtGui
from PySide import QtCore


class LODBoxMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(LODBoxMainWindow, self).__init__()
        # self.centralWidget = LODBoxStartWidget(self)
        self.centralWidget = LODBoxInputWidget(self)
        self.initGui()

    def initGui(self):
        self.setObjectName(self.__class__.__name__)
        self.setWindowTitle("LOD Box")
        self.setMinimumWidth(430)
        self.setMinimumHeight(200)

        self.setCentralWidget(self.centralWidget)
        self.show()


class LODBoxStartWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(LODBoxStartWidget, self).__init__(parent)
        self.parent = self.parentWidget()  # type: LODBoxMainWindow

        self.widget_layout = QtGui.QGridLayout()
        self.title_label = QtGui.QLabel("LOD Box")
        self.title_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.subtitle_label = QtGui.QLabel("A tool for managing LOD Groups")
        self.subtitle_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.recent_files_grp = QtGui.QGroupBox("Recent Files")
        self.recent_files_list = QtGui.QListWidget(self)
        # THE FOLLOWING ARE FOR TESTING ONLY
        temp = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        for x in temp:
            self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example{}.fbx".format(x), self.recent_files_list)

        # END TESTING STUFF

        self.buttons_grp = QtGui.QGroupBox("Actions")
        self.create_btn = QtGui.QPushButton("Create")
        self.manage_btn = QtGui.QPushButton("Manage")

        self.initWidget()

        # self.create_btn.pressed.connect(self.showCreateWidget)
        # self.manage_btn.pressed.connect(self.manageDialog.InitDialog)

    def initWidget(self):
        self.setObjectName(self.__class__.__name__)

        actions_layout = QtGui.QVBoxLayout()
        actions_layout.addWidget(self.create_btn)
        actions_layout.addWidget(self.manage_btn)
        actions_layout.addStretch(1)
        self.buttons_grp.setLayout(actions_layout)

        recent_files_layout = QtGui.QVBoxLayout()
        recent_files_layout.addWidget(self.recent_files_list)
        self.recent_files_grp.setLayout(recent_files_layout)

        self.widget_layout.addWidget(self.title_label, 0, 0, 1, 2)
        self.widget_layout.addWidget(self.subtitle_label, 1, 0, 1, 2)
        self.widget_layout.addWidget(self.recent_files_grp, 2, 0)
        self.widget_layout.addWidget(self.buttons_grp, 2, 1)
        self.setLayout(self.widget_layout)

    def showCreateWidget(self):
        pass


class LODBoxInputWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(LODBoxInputWidget, self).__init__(parent)

        self.parent = self.parentWidget()

        self.layout = QtGui.QVBoxLayout()
        self.title_label = QtGui.QLabel("Inputs")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)

        self.file_input_layout = QtGui.QHBoxLayout()
        self.input_field = QtGui.QLineEdit("Input")
        self.remove_btn = QtGui.QPushButton("Remove")

        self.add_input_btn = QtGui.QPushButton("+")

        self.remove_btn.pressed.connect(self.remove)
        self.add_input_btn.pressed.connect(self.addInput)

        self.initWidget()

    def initWidget(self):
        self.setObjectName(self.__class__.__name__)

        self.file_input_layout.addWidget(self.input_field)
        self.file_input_layout.addWidget(self.remove_btn)

        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.file_input_layout)
        self.layout.addWidget(self.add_input_btn)
        self.setLayout(self.layout)

    def remove(self):
        print("Parent Widget: {}".format(self.parentWidget().objectName()))

    def addInput(self):
        print("Class Name: {}".format(self.__class__.__name__))


# class LODBoxManageDialog(QtGui.QDialog):
#     def __init__(self):
#         super(LODBoxManageDialog, self).__init__()
#
#     def InitDialog(self):
#         self.setWindowTitle("Manage LOD Groups")
#         self.resize(500, 300)
#         self.show()


if __name__ == '__main__':
    try:
        LODBoxApp = QtGui.QApplication(sys.argv)
        LODBox = LODBoxMainWindow()
        LODBoxApp.exec_()
        sys.exit(0)
    except NameError:
        print("Name Error:", sys.exc_info()[1])
    except SystemExit:
        print("Closing LOD Box Window...")
