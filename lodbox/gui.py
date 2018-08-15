import sys
from PySide import QtGui
from PySide import QtCore


class LODBoxMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(LODBoxMainWindow, self).__init__()
        self.centralWidget = LODBoxStartWidget(self)
        self.initGui()

    def initGui(self):
        self.setObjectName("LODBoxMainWindow")
        self.setWindowTitle("LOD Box")
        self.setMinimumWidth(430)
        self.setMinimumHeight(200)

        self.setCentralWidget(self.centralWidget)
        self.show()


class LODBoxStartWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(LODBoxStartWidget, self).__init__(parent)
        self.parent = self.parentWidget()  # type: LODBoxMainWindow
        # self.createInputWidget = LODBoxCreateInputWidget(self.parent)

        self.widget_layout = QtGui.QGridLayout()
        self.title_label = QtGui.QLabel("LOD Box")
        self.title_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.subtitle_label = QtGui.QLabel("A tool for managing LOD Groups")
        self.subtitle_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.recent_files_grp = QtGui.QGroupBox("Recent Files")
        self.recent_files_list = QtGui.QListWidget(self)
        self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example1.fbx", self.recent_files_list)
        self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example2.fbx", self.recent_files_list)
        self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example3.fbx", self.recent_files_list)
        self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example4.fbx", self.recent_files_list)
        self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example5.fbx", self.recent_files_list)
        self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example6.fbx", self.recent_files_list)
        self.test_item = QtGui.QListWidgetItem("D:/Projects/TestProject/Example7.fbx", self.recent_files_list)

        self.buttons_grp = QtGui.QGroupBox("Actions")
        self.create_btn = QtGui.QPushButton("Create")
        self.manage_btn = QtGui.QPushButton("Manage")

        self.initWidget()

        self.create_btn.pressed.connect(self.showCreateWidget)
        # self.manage_btn.pressed.connect(self.manageDialog.InitDialog)

    def initWidget(self):
        self.setObjectName("LODBoxStartWidget")

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


class LODBoxCreateInputWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(LODBoxCreateInputWidget, self).__init__(parent)
        self.parent = self.parentWidget()

        self.layout = QtGui.QVBoxLayout()
        self.test_btn = QtGui.QPushButton("TEST")
        self.test_btn_2 = QtGui.QPushButton("TEST2")

        self.test_btn.pressed.connect(self.test)
        self.test_btn_2.pressed.connect(self.test2)

        self.initWidget()

    def initWidget(self):
        self.setObjectName("LODBoxCreateInputWidget")
        self.layout.addWidget(self.test_btn)
        self.layout.addWidget(self.test_btn_2)
        self.setLayout(self.layout)

    def test(self):
        print(self.parentWidget().objectName())

    def test2(self):
        print(self.parentWidget().centralWidget)

# class LODBoxCreateDialog(QtGui.QDialog):
#     def __init__(self):
#         super(LODBoxCreateDialog, self).__init__()
#
#     def InitDialog(self):
#         self.setWindowTitle("Create LOD Groups")
#         self.resize(500, 300)
#         self.show()
#
#
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
