# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import goes, goes.utils
from itertools import chain
import os
import s3fs

def download(bucket, products, start, end, hours, channels, output, progress=None):
    # Connection with S3 GOES AWS file system
    fs = s3fs.S3FileSystem(anon=True)

    # Build list of days
    days = goes.utils.generateListOfDays(start, end)

    # Searching for files
    files = []
    for product in products:
        if bucket not in product:
            product = bucket + product
        hasChannels = goes.utils.isChannelSeparated(product)
        for day in days:
            for hour in hours:
                if not hasChannels:
                    # search files by day/hour: <product/YYYY/J/HH/*>
                    query = ('{}/{}/{}/{}/*'.format(product,
                        day.strftime('%Y'), day.strftime('%j'), hour)
                    )
                    files.append(fs.glob(query))
                else:
                    for channel in channels:
                        # search files by day/hour/channel: <product/YYYY/J/HH/*>
                        query = ('{}/{}/{}/{}/*C{}*'.format(product,
                            day.strftime('%Y'), day.strftime('%j'), hour, channel) 
                        )
                        files.append(fs.glob(query))

    # Progress notifier
    notifier = goes.utils.Notifier()

    if progress:
        notifier.startDownloadTask.connect(progress.onStartDownloadTask)
        notifier.startFileDownload.connect(progress.onStartFileDownload)
        notifier.endFileDownload.connect(progress.onEndFileDownload)
        notifier.endDownloadTask.connect(progress.onEndDownloadTask)

    # Flat list of files
    files = list(chain.from_iterable(files))

    # Communicate number of files
    notifier.startDownloadTask.emit(len(files))

    # Download each file
    for f in files:
        if progress and progress.wasCanceled():
            break
        notifier.startFileDownload.emit(f)
        # Build local file path
        local = os.path.join(output, f) 
        if os.path.exists(local):
            notifier.endFileDownload.emit(local)
            continue

        # Create local directory, if necessary
        os.makedirs(os.path.dirname(local), exist_ok=True)

        # Download file!
        fs.get(f, local)

        # Notify
        notifier.endFileDownload.emit(local)

    notifier.endDownloadTask.emit()
