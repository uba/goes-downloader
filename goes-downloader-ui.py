# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import goes.widgets
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
app.setStyle('Fusion')
w = goes.widgets.Downloader()
w.show()
sys.exit(app.exec_())
