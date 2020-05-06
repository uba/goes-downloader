# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

# Build hour values (i.e. ['00', '01, ..., '12', .., '20, '23'])
HOURS = [str(i).zfill(2) for i in range(0, 24)]

# Build channel names (i.e. ['01', '02, '03', ..., '15', '16'])
CHANNELS = [str(i).zfill(2) for i in range(1, 17)]

# Define S3 Buckets
BUCKETS = {
    'GOES-16' : 'noaa-goes16/',
    'GOES-17' : 'noaa-goes17/'
}