# -*- coding: utf-8 -*-

import pyperclip
from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_translateWindow(QtWidgets.QMainWindow):
    def copy_clipboard(self, event):
        text = self.translated_text_label.text().strip()
        print(f"Clipboard copy: [{text}]")
        pyperclip.copy(text)

    def __init__(self, opacity_slider):
        super().__init__()
        self.setObjectName("translateWindow")
        self.resize(500, 80)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.translated_text_label = QtWidgets.QLabel(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.translated_text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.translated_text_label, 0, 0, 1, 1)

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setFamilies(['Microsoft YaHei', 'Seagoe UI'])

        self.translated_text_label.setFont(font)
        self.translated_text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.translated_text_label.setObjectName("translated_text_label")
        self.translated_text_label.setWordWrap(True)
        self.translated_text_label.mousePressEvent = self.copy_clipboard

        self.setCentralWidget(self.centralwidget)

        if False:
            self.menubar = QtWidgets.QMenuBar(self)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
            self.menubar.setObjectName("menubar")

            self.setMenuBar(self.menubar)

            self.statusbar = QtWidgets.QStatusBar(self)
            self.statusbar.setObjectName("statusbar")
            self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowFlags(            
            QtCore.Qt.WindowType.Window |
            QtCore.Qt.WindowType.CustomizeWindowHint |
            QtCore.Qt.WindowType.WindowTitleHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowOpacity(opacity_slider.value() / 100)

    def set_worker(self, worker):
        self.worker = worker

    def set_text(self, text):
        self.translated_text_label.setText(text.replace('\n\n', '\n').rstrip())

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("translateWindow", "DeskTranslator"))
        self.translated_text_label.setText(_translate("translateWindow", "Translated text here"))

    def closeEvent(self, event):
        self.worker.stop_running()

    def set_title(self, title: str=''):
        if title:
            self.setWindowTitle(f'DeskTranslator - {title}')
        else:
            self.setWindowTitle('DeskTranslator')

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    translateWindow = QtWidgets.QMainWindow()
    ui = Ui_translateWindow()
    ui.setupUi(translateWindow)
    translateWindow.show()
    sys.exit(app.exec_())
