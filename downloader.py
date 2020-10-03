#!/usr/bin/env python3
""" Downloader for Blender 2.8 daily Linux builds """

import requests
import wget
import subprocess
import sys
import os
from bs4 import BeautifulSoup


# site specific - change as needed
HOME = '/home/steve'
# BLENDER_DIR = HOME + '/blender'
BLENDER_DIR = '/projects/steve/blender'
DOWNLOAD_DIR = HOME + '/Downloads/'

SYMLINK_NAME = 'blender-daily'
LAST_FILENAME = './LAST_DOWNLOAD'


# blender.org specific
DAILY_BUILD_URL = 'https://builder.blender.org/download/'
ROOT_URL = 'https://builder.blender.org'
# html title tag for linux build
#  this changed after 2.80 release
TITLE_PROPERTY = 'Download Linux 64 bit build'


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
    """ is a new build available? """
    try:
        with open(LAST_FILENAME, 'r') as infile:
            last_file = infile.read()
    except FileNotFoundError:
        last_file = None
    if file_name == last_file:
        raise Exception('No new build available')
    return True


def fetch_latest_build(download_link, destination_path):
    download_url = ROOT_URL + download_link
    print('getting: ' + download_url)
    # wget -O destination  url 
    status = subprocess.call( f"wget -O {destination_path} {download_url}",
                              shell=True)
    if status:
        raise Exception(f"wget returned {status}")


if __name__ == '__main__':
    try:
        os.chdir(BLENDER_DIR)
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
        if status:
            raise Exception("tar returned {}".format(status))

        # make directory symlink
        #  cmd = ln -sfn tarfile-basename blender-daily
        cmd = '{} {} {}'.format('ln -sfn',
                                file_name.split('.tar.xz')[0],
                                SYMLINK_NAME)
        status = subprocess.call(cmd, shell=True)
    except Exception as e:
        print(e, file=sys.stderr)
