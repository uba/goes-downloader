# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import argparse
import datetime
import goes, goes.downloader, goes.utils

def parseDate(s):
    try:
        return datetime.datetime.strptime(s, '%Y%m%d')
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == '__main__':
    # Create command-line parser
    parser = argparse.ArgumentParser(description='A tool to download GOES data from AWS.', prog='goes-downloader')
    parser.add_argument('-satellite', '-sat', choices=['GOES-16', 'GOES-17'], type=str, dest='satellite', required=True)
    parser.add_argument('-products', '-p', help='List of products', nargs='+', type=str, dest='products', required=True)
    parser.add_argument('-start', '-s', type=parseDate, help='Start date', dest='start', required=True)
    parser.add_argument('-end', '-e', type=parseDate, help='End date', dest='end', required=False, default=None)
    parser.add_argument('-hours', '-hrs', help='List of hours', nargs='+', type=str, dest='hours', default=goes.HOURS, required=False)
    parser.add_argument('-channels', '-ch', help='List of channels', nargs='+', type=str, dest='channels', default=goes.CHANNELS, required=False)
    parser.add_argument('-output', '-o', help='Path to output directory that will be used to save files', type=str, dest='output', required=True)
    parser.add_argument('-version', '-v', action='version', version='%(prog)s 1.0.0')

    # Parse input
    args = parser.parse_args()

    # Verify dates
    if args.end is None:
        args.end = args.start

    # Download data
    goes.downloader.download(goes.BUCKETS[args.satellite],
        args.products, args.start, args.end, args.hours, args.channels, args.output, goes.utils.TqdmProgress())
