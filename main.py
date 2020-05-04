# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

from PyQt5.QtWidgets import QApplication
import widgets
import sys

app = QApplication(sys.argv)
w = widgets.Downloader()
w.show()
sys.exit(app.exec_())
