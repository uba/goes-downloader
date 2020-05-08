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

## Examples
Download GOES-16 ABI-L1b data (Full-disk), 8 April 2020, 13h, Channels: 01 (VIS), 08 (WV) and 13 (IR).
```bash
goes-downloader.py -satellite GOES-16
                   -products ABI-L1b-RadF
                   -start 20200408 -hours 13
                   -channels 01 08 13
                   -output ./my_output_dir
                   
Download GOES data:   6%|█████     | 1/18 [02:35<43:59, 155.29s/file]
```

Download GOES-16 GLM data, between 8 April 2020 and 10 April 2020, All-hours.
```bash
goes-downloader.py -satellite GOES-16
                   -products GLM-L2-LCFA
                   -start 20200408 -end 20200410
                   -output ./my_output_dir
                   
Download GOES data:   1%|▍   | 68/12960 [00:57<3:01:12,  1.19file/s]
```

## Graphical User-Interface
![](preview/main-ui.png)
![](preview/progress-ui.png) 
