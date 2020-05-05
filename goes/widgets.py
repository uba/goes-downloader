# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import datetime
import goes
from itertools import chain
from PyQt5 import uic
from PyQt5.QtCore import Qt, QDate, QDir
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QMessageBox, QWidget
import s3fs
import sys

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
        self.productListWidget.currentItemChanged.connect(self.__onProductListChanged)
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
        for p in self.fs.ls(self.bucket):
            if 'index.html' not in p:
                self.productListWidget.addItem(p)
        self.productListWidget.setCurrentRow(0)

    def __onSatelliteComboBoxChanged(self, satellite):
        self.bucket = goes.BUCKETS[satellite]
        self.__fillProducts()

    def __onProductListChanged(self, current, previous):
        if current:
            self.hasChannels = 'L1b-Rad' in current.text() or 'L2-CMI' in current.text()
            self.channelGroupBox.setEnabled(self.hasChannels)

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
        product = self.productListWidget.currentItem().text()
        outputdir =  self.outputDirectoryLineEdit.text()
        if not outputdir:
            QMessageBox.information(self, 'Information',
                'Please, select a directory to save files.'
            )
            self.outputDirectoryLineEdit.setFocus()
            return

        hours = self.__getSelectedItems(self.hourListWidget)
        if not hours:
            QMessageBox.information(self, 'Information',
                'Please, select at least one hour.'
            )
            self.hourListWidget.setFocus()
            return

        channels = self.__getSelectedItems(self.channelListWidget)
        if self.hasChannels and not channels:
            QMessageBox.information(self, 'Information',
                'Please, select at least one channel.'
            )
            self.channelListWidget.setFocus()
            return

        start = self.startDateTimeEdit.date().toPyDate()
        end = self.endDateTimeEdit.date().toPyDate()

        days = goes.utils.generateListOfDays(start, end)
        
        # Build list of files that will be download
        files = []
        for day in days:
            for hour in hours:
                if not self.hasChannels:
                    # search files by day/hour: <product/YYYY/J/HH/*>
                    query = ('{}/{}/{}/{}/*'.format(product,
                        day.strftime('%Y'), day.strftime('%j'), hour)
                    )
                    files.append(self.fs.glob(query))
                else:
                    for channel in channels:
                        # search files by day/hour/channel: <product/YYYY/J/HH/*>
                        query = ('{}/{}/{}/{}/*C{}*'.format(product,
                            day.strftime('%Y'), day.strftime('%j'), hour, channel) 
                        )
                        files.append(self.fs.glob(query))

        # Flat list
        files = list(chain.from_iterable(files))
        
        # Download each file
        for f in files:
            print('Downloading', f)
            #self.fs.get(f, outputdir + '/' + f.split('/')[-1])

    def __getSelectedItems(self, listWidget):
        values = []
        for i in range(listWidget.count()):
            item = listWidget.item(i)
            if item.checkState():
                values.append(item.text())
        return values
