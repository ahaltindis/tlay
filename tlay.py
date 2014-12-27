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

import configparser

class Layouts():
    lays = []
    actions = {}
    icons = {}

    def __init__(self, parent = None):
        self.config = configparser.ConfigParser()
        self.parent = parent
        self.load_config()

    def load_config(self):
        if self.config.read('tlay.conf'):
            if 'Layouts' in self.config:
                layouts = self.config['Layouts']
                for index in range(0, len(layouts)):
                    self.add(layouts[str(index)], layouts[str(index)])
            else:
                self.create_config()
        else:
            self.create_config()

    def save_config(self):
        print("save")

    def create_config(self):
        self.config['Layouts'] = {0:'us', 1:'tr'}
        with open('tlay.conf', 'w') as configFile:
            self.config.write(configFile)
        self.load_config()

    def get_all_layouts(self):
        import subprocess
        arr_lays = []
        try:
            str_lays = subprocess.check_output(['localectl',
            'list-x11-keymap-layouts'])
            arr_lays = str_lays.decode("utf-8").split()
        except:
            print("ERROR - Could not get available locales.")
            print("      - You may have missing 'localectl' ")
        return arr_lays

    def add(self, layout, img):
        Layouts.lays.append(layout)
        Layouts.actions[layout] = QAction(layout, self.parent)
        Layouts.icons[layout] = QIcon(img+".png")
        
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
        self.setWindowTitle("TLay - About")
        self.setMaximumSize(250, 300)
        self.setMinimumSize(250, 300)
        self.initForm()

    def initForm(self):
        layHead = QLabel(self)
        layHead.setText("TLay")
        layHead.setStyleSheet("color:red; font-size:25;")

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

        self.layouts = Layouts(self)

        self.tray = SystemTray(QIcon("us.png"), self)

        self.tray.wheelUp.connect(self.wheelUp)
        self.tray.wheelDown.connect(self.wheelDown)
        self.tray.setContextMenu(self.initMenu())
        self.tray.show()

        self.initUI()

    def initUI(self):
        self.layouts_chosen = Layouts.lays
        self.layouts_all = self.layouts.get_all_layouts()

    def initMenu(self):
        menu = QMenu()
        menu.addAction("tlay").setEnabled(False)
        menu.addSeparator()

        langGroup = QActionGroup(menu)

        for lang in Layouts.lays:
            action = Layouts.actions[lang]
            langGroup.addAction(action)
            menu.addAction(action)
            action.triggered.connect(self.changeLang)
            action.setCheckable(True)

        menu.addSeparator()
        settingsAction = menu.addAction("Settings")
        menu.addSeparator()
        aboutAction = menu.addAction("About")
        exitAction = menu.addAction("Exit")

        settingsAction.triggered.connect(self.show)
        aboutAction.triggered.connect(self.about.show)
        exitAction.triggered.connect(self.exitApp)
        return menu

    def wheelUp(self):
        index = self.currentIndex-1
        if index < 0:
            index = len(Layouts.lays)-1
        self.setLang(Layouts.lays[index])

    def wheelDown(self):
        index = self.currentIndex+1
        if index >= len(Layouts.lays):
            index = 0
        self.setLang(Layouts.lays[index])

    def changeLang(self):
        lang = self.sender().text()
        self.setLang(lang)

    def setLang(self, lang):
        self.currentIndex = Layouts.lays.index(lang)
        Layouts.actions[lang].setChecked(True)
        self.tray.setIcon(Layouts.icons[lang])
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

