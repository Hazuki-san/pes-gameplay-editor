# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pes-gameplay-editorKptOFo.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QListView,
    QListWidget,
    QMenu,
    QMenuBar,
    QWidget,
)


class Ui_Editor(object):
    def setupUi(self, Editor):
        if not Editor.objectName():
            Editor.setObjectName("Editor")
        Editor.resize(1280, 720)
        Editor.setMinimumSize(QSize(1280, 720))
        Editor.setMaximumSize(QSize(1280, 720))
        self.actionLoad_18_files = QAction(Editor)
        self.actionLoad_18_files.setObjectName("actionLoad_18_files")
        self.actionSave = QAction(Editor)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QAction(Editor)
        self.actionSave_As.setObjectName("actionSave_As")
        self.centralwidget = QWidget(Editor)
        self.centralwidget.setObjectName("centralwidget")
        self.SectionList = QListWidget(self.centralwidget)
        self.SectionList.setObjectName("SectionList")
        self.SectionList.setGeometry(QRect(10, 45, 200, 640))
        self.ValueList = QListWidget(self.centralwidget)
        self.ValueList.setObjectName("ValueList")
        self.ValueList.setGeometry(QRect(220, 10, 1050, 675))
        self.ValueList.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ValueList.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.ValueList.setFlow(QListView.Flow.LeftToRight)
        self.ValueList.setProperty("isWrapping", True)
        self.ValueList.setGridSize(QSize(512, 64))
        self.FileList = QComboBox(self.centralwidget)
        self.FileList.setObjectName("FileList")
        self.FileList.setGeometry(QRect(10, 10, 200, 25))
        Editor.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Editor)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 22))
        self.menuLoad = QMenu(self.menubar)
        self.menuLoad.setObjectName("menuLoad")
        self.menuSave = QMenu(self.menubar)
        self.menuSave.setObjectName("menuSave")
        Editor.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuLoad.menuAction())
        self.menubar.addAction(self.menuSave.menuAction())
        self.menuLoad.addAction(self.actionLoad_18_files)
        self.menuSave.addAction(self.actionSave)
        self.menuSave.addAction(self.actionSave_As)

        self.retranslateUi(Editor)

        QMetaObject.connectSlotsByName(Editor)

    # setupUi

    def retranslateUi(self, Editor):
        Editor.setWindowTitle(
            QCoreApplication.translate("Editor", "PES Gameplay Editor", None)
        )
        self.actionLoad_18_files.setText(
            QCoreApplication.translate("Editor", "Load 18 files", None)
        )
        self.actionSave.setText(QCoreApplication.translate("Editor", "Save", None))
        self.actionSave_As.setText(
            QCoreApplication.translate("Editor", "Save As...", None)
        )
        self.menuLoad.setTitle(QCoreApplication.translate("Editor", "Load", None))
        self.menuSave.setTitle(QCoreApplication.translate("Editor", "Save", None))

    # retranslateUi
