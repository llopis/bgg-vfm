#!/usr/bin/env python

import sys
import os
import re
import urllib2
from xml.dom import minidom
from pprint import pprint

# http://www.boardgamegeek.com/xmlapi/geeklist/11205

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def getGeeklist(geeklist, filename):
	url = "http://www.boardgamegeek.com/xmlapi/geeklist/" + geeklist
	response = urllib2.urlopen(url)
	#print response.info()
	html = response.read()
	#print html
	response.close()  # best practice to close the file

	text_file = open(filename, "w")
	text_file.write(html)
	text_file.close()
	
	
def getPrice(description):
	m = re.search('\$(\d)+', description)
	if m:
		return m.group(0)
	return ""

def getSold(description):
	m = re.search(r'\bsold|traded|gifted\b', description, re.IGNORECASE)
	if m:
		return True
	return False

def parseData(xmldoc):
	games = []

	itemlist = xmldoc.getElementsByTagName('item') 
	#print len(itemlist)
	for s in itemlist :
		game = {}
		game['title'] = s.attributes['objectname'].value
		game['gameid'] = s.attributes['objectid'].value
		game['seller'] = s.attributes['username'].value
		game['itemid'] = str(s.attributes['id'].value)
		body = s.getElementsByTagName("body")[0]
		game['description'] = getText(body.childNodes)
		game['price'] = getPrice(game['description'])
		game['sold'] = getSold(game['description'])
		games.append(game)

	sortedGames = sorted(games, key=lambda k: k['title'])
	
	title = xmldoc.getElementsByTagName("title")[0]
	vfm = {'title' : getText(title.childNodes), 'games' : sortedGames }
	
	return vfm


def generateStaticFiles(vfm, geeklist):
	filename = "geeklist_" + geeklist + ".html"
	fout = open(filename, "w")
	
	fout.write('<html><head><title>' + vfm['title'] + '</title>\n')
	fout.write('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">\n' +
				'<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap-theme.min.css">\n' +
				'<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script>\n')
	fout.write('</head><body>\n')
	fout.write('<h1><a href="https://boardgamegeek.com/geeklist/' + geeklist + '">'  + vfm['title'] + '</a></h1>\n')
	fout.write('<table>\n');
	for game in vfm['games']:
		url = "https://boardgamegeek.com/geeklist/" + geeklist + "/item/" + game['itemid'] + "#item" + game['itemid']
		tagStart = ""
		tagEnd = ""
		if (game['sold']):
			tagStart = '<strike>'
			tagEnd = '</strile>'
		fout.write('<tr>\n')
		fout.write('<td><a href="' + url + '">' + tagStart + game['title'].encode('utf-8') + tagEnd + '</a></td>\n')
		fout.write('<td>' + tagStart + game['price'] + tagEnd + '</td>\n')
		fout.write('<td><a href="https://boardgamegeek.com/user/' + game['seller'] + '">' + tagStart + game['seller'] + tagEnd + '</a></td>\n')
		fout.write('</tr>\n')
	fout.write("</table>\n");

	fout.write('</body></html>\n')

	fout.close()


def generateVFM(geeklist):
	filename = "geeklist_" + geeklist + ".xml"
	#getGeeklist(geeklist, filename)
	
	xmldoc = minidom.parse(filename)

	vfm = parseData(xmldoc)

	generateStaticFiles(vfm, geeklist)	
    
if __name__ == '__main__':
    try:
		geeklist = sys.argv[1]
		generateVFM(geeklist)
    except IndexError:
        print "Usage: %s <geeklist_id>" % sys.argv[0]
        raise SystemExit

