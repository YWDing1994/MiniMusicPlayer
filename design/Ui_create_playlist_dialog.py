# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Code\MyProject\MiniMusicPlayer\design\create_playlist_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_createPlaylistDialog(object):
    def setupUi(self, createPlaylistDialog):
        createPlaylistDialog.setObjectName("createPlaylistDialog")
        createPlaylistDialog.resize(500, 250)
        createPlaylistDialog.setMinimumSize(QtCore.QSize(500, 250))
        createPlaylistDialog.setMaximumSize(QtCore.QSize(500, 250))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(createPlaylistDialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.closeBtn = QtWidgets.QPushButton(createPlaylistDialog)
        self.closeBtn.setMinimumSize(QtCore.QSize(28, 28))
        self.closeBtn.setMaximumSize(QtCore.QSize(28, 28))
        self.closeBtn.setText("")
        self.closeBtn.setObjectName("closeBtn")
        self.horizontalLayout_4.addWidget(self.closeBtn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        spacerItem1 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.userPlaylistLbl = QtWidgets.QLabel(createPlaylistDialog)
        self.userPlaylistLbl.setMinimumSize(QtCore.QSize(64, 64))
        self.userPlaylistLbl.setMaximumSize(QtCore.QSize(64, 64))
        self.userPlaylistLbl.setText("")
        self.userPlaylistLbl.setObjectName("userPlaylistLbl")
        self.horizontalLayout.addWidget(self.userPlaylistLbl)
        self.userPlaylistLnedit = QtWidgets.QLineEdit(createPlaylistDialog)
        self.userPlaylistLnedit.setMinimumSize(QtCore.QSize(256, 28))
        self.userPlaylistLnedit.setMaximumSize(QtCore.QSize(16777215, 28))
        self.userPlaylistLnedit.setObjectName("userPlaylistLnedit")
        self.horizontalLayout.addWidget(self.userPlaylistLnedit)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem4 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout_2.addItem(spacerItem4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem5)
        self.cancelBtn = QtWidgets.QPushButton(createPlaylistDialog)
        self.cancelBtn.setMinimumSize(QtCore.QSize(150, 56))
        self.cancelBtn.setMaximumSize(QtCore.QSize(150, 56))
        self.cancelBtn.setObjectName("cancelBtn")
        self.horizontalLayout_3.addWidget(self.cancelBtn)
        self.okBtn = QtWidgets.QPushButton(createPlaylistDialog)
        self.okBtn.setMinimumSize(QtCore.QSize(150, 56))
        self.okBtn.setMaximumSize(QtCore.QSize(150, 56))
        self.okBtn.setObjectName("okBtn")
        self.horizontalLayout_3.addWidget(self.okBtn)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        spacerItem7 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout_2.addItem(spacerItem7)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.retranslateUi(createPlaylistDialog)
        QtCore.QMetaObject.connectSlotsByName(createPlaylistDialog)

    def retranslateUi(self, createPlaylistDialog):
        _translate = QtCore.QCoreApplication.translate
        createPlaylistDialog.setWindowTitle(_translate("createPlaylistDialog", "Dialog"))
        self.userPlaylistLnedit.setPlaceholderText(_translate("createPlaylistDialog", "请输入要创建的歌单名"))
        self.cancelBtn.setText(_translate("createPlaylistDialog", "取消"))
        self.okBtn.setText(_translate("createPlaylistDialog", "确定"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    createPlaylistDialog = QtWidgets.QDialog()
    ui = Ui_createPlaylistDialog()
    ui.setupUi(createPlaylistDialog)
    createPlaylistDialog.show()
    sys.exit(app.exec_())
