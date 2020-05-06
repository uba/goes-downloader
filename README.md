# goes-downloader
Python application that can be used to download GOES imagery on Amazon Web Service (AWS) S3 Storage.

GOES on AWS: https://registry.opendata.aws/noaa-goes/

Command-line tool and Graphical User-Interface available.

## Usage
```
goes-downloader.py [-h] -satellite {GOES-16,GOES-17}
                        -products PRODUCTS [PRODUCTS ...]
                        -start YYYYMMDD [-end YYYYMMDD]
                        [-hours HOURS [HOURS ...]]
                        [-channels CHANNELS [CHANNELS ...]]
                        -output OUTPUT
                        [-version]

A tool to download GOES data from AWS.

optional arguments:
  -h, --help            show this help message and exit
  -satellite {GOES-16,GOES-17}, -sat {GOES-16,GOES-17}
  -products PRODUCTS [PRODUCTS ...], -p PRODUCTS [PRODUCTS ...] List of products
  -start START, -s START Start date
  -end END, -e END       End date
  -hours HOURS [HOURS ...], -hrs HOURS [HOURS ...] List of hours
  -channels CHANNELS [CHANNELS ...], -ch CHANNELS [CHANNELS ...] List of channels
  -output OUTPUT, -o OUTPUT Path to output directory that will be used to save files
  -version, -v show program's version number and exit
```

## Graphical User-Interface
![](preview/main-ui.png)
![](preview/progress-ui.png) 
