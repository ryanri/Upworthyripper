#!/usr/bin/env python2
"""
Upworthy Ripper
The idea is to take a link to upworthy, and harvest the content it's
repackaged under the upworthy brand. Should give back a youtube link
or something similar
"""
# Accepts Upworthy link as input, hands back a link to the content.
# Makes a rough-and-ready attempt at giving you back the original site,
# rather than just the iframe.

import re
import urllib2
import argparse
from bs4 import BeautifulSoup

logfile = './.upworthyLog'


# Confirm the link is to the correct site
def check_domain(url):
    """
    Checks the domain is correct
    """
    upworthy_re = re.compile(r'^(?:https?://)?(?:www\.)?'
                             '(upworthy.com/.*)\??.*$')
    matches = upworthy_re.match(url)
    if matches:
        return matches.group(1)
    else:
        return None


# Turn extracted content link into something nice & not full browser window.
# Hopefully fail non-terribly.
def find_link(link):
    """
    Finds the tasty content inside the upworthy page
    """
    youtube_re = re.compile(
        r'^(?:(?:http:)|(?:https:))?//(?:www\.)?youtube.com/embed/(.*?)\?.*$')
    vimeo_re = re.compile(
        r'^//player.vimeo.com/video/(\d*)\?.*$')
    kickstart_re = re.compile(
        r'^(https://www.kickstarter.com/projects/\d*/.*)/widget/video.html')
    frame_re = re.compile(r'^//(.*)$')
    youtube = youtube_re.match(link)
    vimeo = vimeo_re.match(link)
    kickstart = kickstart_re.match(link)
    some_frame = frame_re.match(link)
    if youtube:
        vid_url = 'https://www.youtube.com/watch?v='+youtube.group(1)
    elif vimeo:
        vid_url = 'https://www.vimeo.com/'+vimeo.group(1)
    elif kickstart:
        vid_url = kickstart.group(1)
    elif some_frame:
        vid_url = some_frame.group(1)
    else:
        vid_url = link
    return vid_url


# Confirm the link is a valid URL, the easy way - by fetching it.
def check_link(url):
    """
    Confirms the link is good
    """
    page = urllib2.urlopen(url)
    if page.getcode() == 200:
        return page.geturl()
    else:
        with open(logfile, "a") as logfd:
            logfd.write("Upworthy page: {0}\n"
                        "Actual link: {1}\n"
                        "HTTP response: {2}\n"
                        "---\n".format(url, page.geturl(), page.getcode()))
        return "Couldn't extract a valid link; see {0}".format(logfile)


# Get the Upworthy page, harvest the content link.
def get_content(url):
    """
    Some docstring
    """
    soup = BeautifulSoup(urllib2.urlopen("https://www."+url))
    frame = soup.find('iframe')
    if frame is None:       # cope with images
        img = soup.select('#nuggetBody img')
        link = "http:"+img[0].get('src')
    else:
        link = frame.get('src')
    return link


def main():
    """
    main method
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--logfile', nargs='?', default='./.upworthyLog',
                        help='file to log any failures to. Default is '
                             '.upworthyLog in the current directory.')

    parser.add_argument('link', help='Upworthy page to extract content from')
    args = parser.parse_args()
    global logfile
    logfile = args.logfile
    page = check_domain(args.link)
    if page is not None:
        url = get_content(page)
        url = find_link(url)
        url = check_link(url)
        print url

# Parse args, run thing, profit.
if __name__ == '__main__':
    main()
