#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib2
import sys
import re
import sqlite3
import roman


def main():

    who = sys.argv[1]

    url = 'http://swgoh.gg/u/%s/collection/' % who

    req = urllib2.Request(url, headers={'User-Agent': 'Wget/1.17.1'})
    r = urllib2.urlopen(req).read()
    soup = BeautifulSoup(r, "lxml")

    conn = sqlite3.connect('sqlite-db-location')
    c = conn.cursor()
    c.execute("DELETE from toons where user = '%s'" % who)
    for link in soup.find_all("a", "char-portrait-full-link"):
        match = re.search("(light|dark)", link.parent.parent.attrs['class'][1])
        if match:
            side = match.group(1)
        for div in link.find_all("div", "char-portrait-full-level"):
            level = str(div.contents[0])
        for div in link.find_all("div", "char-portrait-full-gear-level"):
            gear = roman.fromRoman(div.contents[0])
        for div in link.select("[class~=star]"):
            if len(div["class"]) < 3:
                star = div["class"][1].lstrip("star")
        values = (who, link.img["alt"], level, gear, star, side)
        c.execute("INSERT INTO toons VALUES (?,?,?,?,?,?)", values)

    for link in soup.find_all("a", "char-portrait-link"):
        match = re.search("(light|dark)", link.parent.parent.attrs['class'][2])
        if match:
            side = match.group(1)
        values = (who, link.img["alt"], 0, 0, 0, side)
        c.execute("INSERT INTO toons VALUES (?,?,?,?,?,?)", values)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
