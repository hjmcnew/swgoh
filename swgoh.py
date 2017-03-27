#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib2

url = 'http://swgoh.gg/u/<profilename>/collection/'

req = urllib2.Request(url, headers={'User-Agent': 'Wget/1.17.1'})
r = urllib2.urlopen(req).read()
soup = BeautifulSoup(r)

for link in soup.find_all("a", "char-portrait-full-link"):
    for div in link.find_all("div", "char-portrait-full-level"):
        level = str(div.contents[0])
    for div in link.find_all("div", "char-portrait-full-gear-level"):
        gear = str(div.contents[0])
    for div in link.select("[class~=star]"):
        if len(div["class"]) < 3:
            star = div["class"][1]
    print ("%s %s %s %s" % (link.img["alt"], level, gear, star))

for link in soup.find_all("a", "char-portrait-link"):
    print ("%s - %s" % (link.img["alt"], 'Inactive'))
