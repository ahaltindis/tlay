#!/bin/python
#-------------------------------------------------#
##--TLay--                                        #
#-------------------------------------------------#
##Version: 1.0                                    #
#                                                 #
##Author: Ahmet ALTINDIS <ahaltindis@gmail.com>   #
##Licence:                                        #
#-------------------------------------------------#

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class Languages():
    langs = []
    actions = {}
    icons = {}

    def __init__(self):
        self.load()

    def load(self):
        print("load")

    def save(self):
        print("save")

    def add(self, lang, img, parent):
        Languages.langs.append(lang)
        Languages.actions[lang] = QAction(lang, parent)
        Languages.icons[lang] = QIcon(img)
        
class SystemTray(QSystemTrayIcon):
    wheelUp = pyqtSignal()
    wheelDown = pyqtSignal()

    def __init__(self, icon, parent = None):
        super(SystemTray, self).__init__(icon, parent)
    
    def event(self, event):
        if event.angleDelta().y() > 0:
            self.wheelUp.emit()
        else:
            self.wheelDown.emit()
        return True

class AboutForm(QWidget):
    def __init__(self, parent = None):
        super(AboutForm, self).__init__(parent)
        layHead = QLabel(self)
        layHead.setText("tlay")
        layHead.setStyleSheet("color:red; font-size:25;")
        self.setWindowTitle("About")
        self.setMaximumSize(250, 300)
        self.setMinimumSize(250, 300)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

class MainForm(QWidget):
    currentIndex = -1;

    def __init__(self, parent = None):
        super(MainForm, self).__init__(parent)

        self.displayWidth = QGuiApplication.screens()[0].geometry().width()
        self.displayHeight = QGuiApplication.screens()[0].geometry().height()

        self.move((self.displayWidth-self.size().width())/2, 
                (self.displayHeight-self.size().height())/4)

        self.about = AboutForm()
        self.about.move((self.displayWidth-self.about.size().width())/2, 
                (self.displayHeight-self.about.size().height())/4)

        self.languages = Languages()
        self.languages.add("us", "us.png", self)
        self.languages.add("tr", "tr.png", self)
        self.languages.add("de", "de.png", self)

        self.tray = SystemTray(QIcon("us.png"), self)

        self.tray.wheelUp.connect(self.wheelUp)
        self.tray.wheelDown.connect(self.wheelDown)
        self.tray.setContextMenu(self.initMenu())
        self.tray.show()

    def initMenu(self):
        menu = QMenu()
        menu.addAction("tlay").setEnabled(False)
        menu.addSeparator()

        langGroup = QActionGroup(menu)

        for lang in Languages.langs:
            action = Languages.actions[lang]
            langGroup.addAction(action)
            menu.addAction(action)
            action.triggered.connect(self.changeLang)
            action.setCheckable(True)

        menu.addSeparator()
        settingsAction = menu.addAction("Settings")
        menu.addSeparator()
        aboutAction = menu.addAction("About")
        exitAction = menu.addAction("Exit")

        aboutAction.triggered.connect(self.about.show)
        exitAction.triggered.connect(self.exitApp)
        return menu

    def wheelUp(self):
        index = self.currentIndex-1
        if index < 0:
            index = len(Languages.langs)-1
        self.setLang(Languages.langs[index])

    def wheelDown(self):
        index = self.currentIndex+1
        if index >= len(Languages.langs):
            index = 0
        self.setLang(Languages.langs[index])

    def changeLang(self):
        lang = self.sender().text()
        self.setLang(lang)

    def setLang(self, lang):
        self.currentIndex = Languages.langs.index(lang)
        Languages.actions[lang].setChecked(True)
        self.tray.setIcon(Languages.icons[lang])
        self.commandLang(lang)

    def commandLang(self, lang):
        import os
        os.system("setxkbmap -layout " + lang)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def exitApp(self):
        app.exit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main_form = MainForm()
    main_form.setWindowTitle("TLay - Settings")
    sys.exit(app.exec_())

