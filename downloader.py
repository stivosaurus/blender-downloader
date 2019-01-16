#!/usr/bin/env python3
""" Downloader for Blender daily Linux builds """

import requests
import wget
# import shutil
import subprocess
import sys
from bs4 import BeautifulSoup


DAILY_BUILD_URL = 'https://builder.blender.org/download/'
ROOT_URL = 'https://builder.blender.org'
TITLE_PROPERTY = 'Download Dev Linux 64 bit master'
DOWNLOAD_DIR = '/home/steve/Downloads/'
LAST_FILENAME = './LAST_DOWNLOAD'


def parse_webpage_for_link(url):
    """
    download and parse daily builds webpage.
    returns download link as string.
    """
    response = requests.get(DAILY_BUILD_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    tags = [x['href'] for x in soup.find_all('a') if
            x.has_attr('title') and x['title'] == TITLE_PROPERTY]
    if not tags:
        raise Exception('no tags found on webpage')
    return tags[0]


def new_build_available(file_name):
    """ is new build available? """
    last_file = None
    try:
        with open(LAST_FILENAME, 'r') as infile:
            last_file = infile.read()
    except FileNotFoundError:
        pass
    if file_name == last_file:
        raise Exception('No new build available')
    return True


def fetch_latest_build(download_link, destination_path):
    download_url = ROOT_URL + download_link
    print('getting: ' + download_url)
    wget.download(download_url, destination_path)
    # same as wget, but using requests and shutil
    # resp = requests.get(download_url, stream=True)
    # with open(file_name, 'wb') as ofile:
    #     shutil.copyfileobj(resp.raw, ofile)


if __name__ == '__main__':
    try:
        # download the tarball
        download_link = parse_webpage_for_link(DAILY_BUILD_URL)
        file_name = download_link.split('/')[-1:][0]
        print('latest build is: ' + file_name)
        destination_path = DOWNLOAD_DIR + file_name
        if new_build_available(file_name):
            fetch_latest_build(download_link, destination_path)
            # store last download filename
            with open(LAST_FILENAME, 'w') as outfile:
                outfile.write(file_name)

        # untar downloaded tarball
        status = subprocess.call('tar xvf ' + destination_path, shell=True)
        # print("tar returned " + str(status))

        # make symlink
        status = subprocess.call('./make-link ' +
                                 file_name.split('.tar.bz2')[:1][0],
                                 shell=True)
    except Exception as e:
        print(e, file=sys.stderr)
