import sys
from PySide2 import QtWidgets
from PySide2 import QtCore


class LODBoxMainWindow(QtWidgets.QMainWindow):
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


class LODBoxStartWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(LODBoxStartWidget, self).__init__(parent)
        self.parent = self.parentWidget()  # type: LODBoxMainWindow
        self.setObjectName(self.__class__.__name__)

        widget_layout = QtWidgets.QGridLayout()
        title_label = QtWidgets.QLabel("LOD Box")
        title_label.setAlignment(QtCore.Qt.AlignHCenter)
        subtitle_label = QtWidgets.QLabel("A tool for managing LOD Groups")
        subtitle_label.setAlignment(QtCore.Qt.AlignHCenter)

        recent_files_grp = QtWidgets.QGroupBox("Recent Files")
        recent_files_list = QtWidgets.QListWidget(self)
        # THE FOLLOWING ARE FOR TESTING ONLY
        for x in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            self.test_item = QtWidgets.QListWidgetItem(F"D:/Projects/TestProject/Example{x}.fbx", recent_files_list)

        # END TESTING STUFF

        buttons_grp = QtWidgets.QGroupBox("Actions")
        create_btn = QtWidgets.QPushButton("Create")
        manage_btn = QtWidgets.QPushButton("Manage")

        actions_layout = QtWidgets.QVBoxLayout()
        actions_layout.addWidget(create_btn)
        actions_layout.addWidget(manage_btn)
        actions_layout.addStretch(1)
        buttons_grp.setLayout(actions_layout)

        recent_files_layout = QtWidgets.QVBoxLayout()
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


class LODBoxInputWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(LODBoxInputWidget, self).__init__(parent)
        self.parent = self.parentWidget()
        self.setObjectName(self.__class__.__name__)

        main_layout = QtWidgets.QVBoxLayout()
        title_label = QtWidgets.QLabel("Inputs")
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        file_input_layout = QtWidgets.QHBoxLayout()
        input_field = QtWidgets.QLineEdit("Input")
        remove_btn = QtWidgets.QPushButton("Remove")

        add_input_btn = QtWidgets.QPushButton("+")

        remove_btn.pressed.connect(self.remove)
        add_input_btn.pressed.connect(self.addInput)

        file_input_layout.addWidget(input_field)
        file_input_layout.addWidget(remove_btn)

        main_layout.addWidget(title_label)
        main_layout.addLayout(file_input_layout)
        main_layout.addWidget(add_input_btn)
        self.setLayout(main_layout)

    def remove(self):
        print(F"Parent Widget: {self.parentWidget().objectName()}")

    def addInput(self):
        print(F"Class Name: {self.__class__.__name__}")


# class LODBoxManageDialog(QtWidgets.QDialog):
#     def __init__(self):
#         super(LODBoxManageDialog, self).__init__()
#
#     def InitDialog(self):
#         self.setWindowTitle("Manage LOD Groups")
#         self.resize(500, 300)
#         self.show()


if __name__ == '__main__':
    try:
        LODBoxApp = QtWidgets.QApplication(sys.argv)
        LODBox = LODBoxMainWindow()
        LODBoxApp.exec_()
        sys.exit(0)
    except NameError:
        print("Name Error:", sys.exc_info()[1])
    except SystemExit:
        print("Closing LOD Box Window...")
