#!/usr/bin/env python2

# Accepts Upworthy link as input, hands back a link to the content.
# Makes a rough-and-ready attempt at giving you back the original site,
# rather than just the iframe.

import re
import sys
import urllib2
import argparse
from bs4 import BeautifulSoup


# Confirm the link is to the correct site
def checkDomain(url):
    upworthyRe = re.compile('^(?:https?://)?(?:www\.)?(upworthy.com/.*)\??.*$')
    matches = upworthyRe.match(url)
    if matches:
        return matches.group(1)
    else:
        return None


# Turn extracted content link into something nice & not full browser window.
# Hopefully fail non-terribly.
def findLink(link):
    youtubeRe = re.compile(
        '^(?:(?:http:)|(?:https:))?//(?:www\.)?youtube.com/embed/(.*?)\?.*$')
    vimeoRe = re.compile(
        '^//player.vimeo.com/video/(\d*)\?.*$')
    kickstartRe = re.compile(
        '^(https://www.kickstarter.com/projects/\d*/.*)/widget/video.html')
    frameRe = re.compile('^//(.*)$')
    youtube = youtubeRe.match(url)
    vimeo = vimeoRe.match(url)
    kickstart = kickstartRe.match(url)
    someFrame = frameRe.match(url)
    if youtube:
        vidUrl = 'https://www.youtube.com/watch?v='+youtube.group(1)
    elif vimeo:
        vidUrl = 'https://www.vimeo.com/'+vimeo.group(1)
    elif kickstart:
        vidUrl = ks.group(1)
    elif someFrame:
        vidUrl = someFrame.group(1)
    else:
        vidUrl = url
    return vidUrl


# Confirm the link is a valid URL, the easy way - by fetching it.
def checkLink(url):
    page = urllib2.urlopen(url)
    if (page.getcode() == 200):
        return page.geturl()
    else:
        with open(logfile, "a") as f:
            f.write("Upworthy page: "+upworthyPage+"\nAttempted link: "+vidUrl
                    + "\nActual link: "+page.geturl()+"\n HTTP response: "
                    + str(page.getcode())+"\n---\n")
        return "Couldn't extract a valid link; see "+logfile


# Get the Upworthy page, harvest the content link.
def getContent(url):
    soup = BeautifulSoup(urllib2.urlopen("https://www."+url))
    frame = soup.find('iframe')
    if frame is None:       # cope with images
        img = soup.select('#nuggetBody img')
        link = "http:"+img[0].get('src')
    else:
        link = frame.get('src')
    return link


# Parse args, run thing, profit.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--logfile', nargs='?', default='./.upworthyLog',
            help='file to log any failures to. Default is .upworthyLog in the current directory.')

    parser.add_argument('link', help='Upworthy page to extract content from')
    args = parser.parse_args()
    logfile = args.logfile
    page = checkDomain(args.link)
    if page is not None:
        url = getContent(page)
        url = findLink(url)
        url = checkLink(url)
        print url
