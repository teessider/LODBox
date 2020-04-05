import sys
from PySide import QtGui
from PySide import QtCore


class LODBoxMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(LODBoxMainWindow, self).__init__()
        self.setObjectName(self.__class__.__name__)

        self.centralWidget = LODBoxStartWidget(self)
        # self.centralWidget = LODBoxInputWidget(self)

        self.setWindowTitle("LOD Box")
        self.setMinimumWidth(430)
        self.setMinimumHeight(200)

        self.setCentralWidget(self.centralWidget)
        self.show()


class LODBoxStartWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(LODBoxStartWidget, self).__init__(parent)
        self.parent = self.parentWidget()  # type: LODBoxMainWindow
        self.setObjectName(self.__class__.__name__)

        widget_layout = QtGui.QGridLayout()
        title_label = QtGui.QLabel("LOD Box")
        title_label.setAlignment(QtCore.Qt.AlignHCenter)
        subtitle_label = QtGui.QLabel("A tool for managing LOD Groups")
        subtitle_label.setAlignment(QtCore.Qt.AlignHCenter)

        recent_files_grp = QtGui.QGroupBox("Recent Files")
        recent_files_list = QtGui.QListWidget(self)
        # THE FOLLOWING ARE FOR TESTING ONLY
        for x in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example{}.fbx".format(x), recent_files_list)

        # END TESTING STUFF

        buttons_grp = QtGui.QGroupBox("Actions")
        create_btn = QtGui.QPushButton("Create")
        manage_btn = QtGui.QPushButton("Manage")

        actions_layout = QtGui.QVBoxLayout()
        actions_layout.addWidget(create_btn)
        actions_layout.addWidget(manage_btn)
        actions_layout.addStretch(1)
        buttons_grp.setLayout(actions_layout)

        recent_files_layout = QtGui.QVBoxLayout()
        recent_files_layout.addWidget(recent_files_list)
        recent_files_grp.setLayout(recent_files_layout)

        widget_layout.addWidget(title_label, 0, 0, 1, 2)
        widget_layout.addWidget(subtitle_label, 1, 0, 1, 2)
        widget_layout.addWidget(recent_files_grp, 2, 0)
        widget_layout.addWidget(buttons_grp, 2, 1)
        self.setLayout(widget_layout)

        # create_btn.pressed.connect(self.showCreateWidget)
        # manage_btn.pressed.connect(self.manageDialog.InitDialog)

    def showCreateWidget(self):
        pass


class LODBoxInputWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(LODBoxInputWidget, self).__init__(parent)
        self.parent = self.parentWidget()
        self.setObjectName(self.__class__.__name__)

        main_layout = QtGui.QVBoxLayout()
        title_label = QtGui.QLabel("Inputs")
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        file_input_layout = QtGui.QHBoxLayout()
        input_field = QtGui.QLineEdit("Input")
        remove_btn = QtGui.QPushButton("Remove")

        add_input_btn = QtGui.QPushButton("+")

        remove_btn.pressed.connect(self.remove)
        add_input_btn.pressed.connect(self.addInput)

        file_input_layout.addWidget(input_field)
        file_input_layout.addWidget(remove_btn)

        main_layout.addWidget(title_label)
        main_layout.addLayout(file_input_layout)
        main_layout.addWidget(add_input_btn)
        self.setLayout(main_layout)

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
