# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import goes, goes.downloader
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import s3fs

class Downloader(QWidget):
    def __init__(self):
        super(Downloader, self).__init__()
        # Load user-interface from ui file
        uic.loadUi('./ui/downloader.ui', self)

        # Setup buckets
        for bucket in goes.BUCKETS:
            self.satelliteComboBox.addItem(bucket)
            
        # Define default bucket
        self.bucket = goes.BUCKETS['GOES-16']

        # Populate hours
        for hour in goes.HOURS:
            item = QListWidgetItem(hour, self.hourListWidget, Qt.ItemIsUserCheckable);
            item.setCheckState(Qt.Checked)

        # Populate channels
        for channel in goes.CHANNELS:
            item = QListWidgetItem(channel, self.channelListWidget, Qt.ItemIsUserCheckable);
            item.setCheckState(Qt.Checked)

        # Flag that indicates if selected product is channel-separated
        self.hasChannels = True

        # Setup initial dates
        now = QDate.currentDate()
        self.startDateTimeEdit.setDate(now)
        self.endDateTimeEdit.setMaximumDate(now)
        self.endDateTimeEdit.setDate(now)

        # Setup output directory
        self.outputDirectoryLineEdit.setText(QDir.currentPath())

        # Signals & slots
        self.satelliteComboBox.currentTextChanged[str].connect(self.__onSatelliteComboBoxChanged)
        self.productsCheckBox.stateChanged.connect(self.__onProductsCheckBoxChanged)
        self.hoursCheckBox.stateChanged.connect(self.__onHoursCheckBoxChanged)
        self.channelsCheckBox.stateChanged.connect(self.__onChannelsCheckBoxChanged)
        self.outputDirectoryPushButton.released.connect(self.__onOutputDirectoryPushButtonReleased)
        self.downloadPushButton.released.connect(self.__onDownloadPushButtonReleased)

        # Connection with S3 GOES-16 AWS file system
        self.fs = s3fs.S3FileSystem(anon=True)

        # Fill product list
        self.__fillProducts()
    
    def __fillProducts(self):
        self.productListWidget.clear()
        for product in self.fs.ls(self.bucket):
            if 'index.html' not in product:
                item = QListWidgetItem(product, self.productListWidget, Qt.ItemIsUserCheckable);
                item.setCheckState(Qt.Unchecked)
        self.productListWidget.setCurrentRow(0)

    def __onSatelliteComboBoxChanged(self, satellite):
        self.bucket = goes.BUCKETS[satellite]
        self.__fillProducts()

    def __onProductsCheckBoxChanged(self, state):
        for i in range(self.hourListWidget.count()):
            self.productListWidget.item(i).setCheckState(state)

    def __onHoursCheckBoxChanged(self, state):
        for i in range(self.hourListWidget.count()):
            self.hourListWidget.item(i).setCheckState(state)

    def __onChannelsCheckBoxChanged(self, state):
        for i in range(self.channelListWidget.count()):
            self.channelListWidget.item(i).setCheckState(state)

    def __onOutputDirectoryPushButtonReleased(self): 
        self.outputDirectoryLineEdit.setText(
            QFileDialog.getExistingDirectory(self, 'Output Directory', '.')
        )

    def __onDownloadPushButtonReleased(self):
        # Verify selected products
        products = self.__getSelectedItems(self.productListWidget)
        if not products:
            QMessageBox.information(self, 'Information',
                'Please, select at least one product.'
            )
            self.productListWidget.setFocus()
            return

        # Verify selected hours
        hours = self.__getSelectedItems(self.hourListWidget)
        if not hours:
            QMessageBox.information(self, 'Information',
                'Please, select at least one hour.'
            )
            self.hourListWidget.setFocus()
            return

        # Verify selected channels
        channels = self.__getSelectedItems(self.channelListWidget)
        if self.hasChannels and not channels:
            QMessageBox.information(self, 'Information',
                'Please, select at least one channel.'
            )
            self.channelListWidget.setFocus()
            return

        # Verify output directory
        output =  self.outputDirectoryLineEdit.text()
        if not output:
            QMessageBox.information(self, 'Information',
                'Please, select a directory to save files.'
            )
            self.outputDirectoryLineEdit.setFocus()
            return
        
        # Get selected dates
        start = self.startDateTimeEdit.date().toPyDate()
        end = self.endDateTimeEdit.date().toPyDate()

        progress = ProgressDialog(self)

        # Start search and download
        download = ProcessRunnable(target=goes.downloader.download,
                        args=(self.bucket, products, start, end, hours, channels, output, progress))

        download.start()

        progress.exec()

    def __getSelectedItems(self, listWidget):
        values = []
        for i in range(listWidget.count()):
            item = listWidget.item(i)
            if item.checkState():
                values.append(item.text())
        return values

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super(ProgressDialog, self).__init__(parent=parent)
        # Load user-interface from ui file
        uic.loadUi('./ui/progress.ui', self)
        # Flag that indicates if process was canceled
        self.canceled = False
        # Signal & slots
        self.cancelPushButton.released.connect(self.onCancelPushButtonReleased)

    @pyqtSlot(int)
    def onStartDownloadTask(self, numberOfFiles):
        self.progressBar.setMaximum(numberOfFiles)
        self.progressBar.setValue(0)

    @pyqtSlot(str)
    def onStartFileDownload(self, file):
        self.__appendText(('- Downloading {}'.format(file.split('/')[-1])))

    @pyqtSlot(str)
    def onEndFileDownload(self, file):
        self.__appendText(('* Finished -> {}'.format(file)))
        self.progressBar.setValue(self.progressBar.value() + 1)

    @pyqtSlot()
    def onEndDownloadTask(self):
        self.__appendText('Done!')
        self.progressBar.setValue(self.progressBar.maximum())
        QApplication.restoreOverrideCursor()

    def onCancelPushButtonReleased(self):
        self.canceled = True
        self.__appendText('\n*** Aborting. Please, wait... ***')
        self.cancelPushButton.setDisabled(True)
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def wasCanceled(self):
        return self.canceled

    def __appendText(self, text):
        self.notificationPlainTextEdit.appendPlainText(text)
        scrool = self.notificationPlainTextEdit.verticalScrollBar()
        scrool.setValue(scrool.maximum())

class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args
        self.setAutoDelete(True)

    def __del__(self):
        QThreadPool.globalInstance().waitForDone()

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)
