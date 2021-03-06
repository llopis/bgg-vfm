#!/usr/bin/env python

import sys
import os
import re
import urllib2
import time
import shutil
from xml.dom import minidom
from pprint import pprint


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc).encode('utf-8')


def getGeeklist(geeklist, filename):
	url = "http://www.boardgamegeek.com/xmlapi/geeklist/" + geeklist + "?random=" + str(time.time())
	#response = urllib2.urlopen(url)
	#html = response.read()
	#response.close()
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0')
	response = urllib2.build_opener().open(request)
	html = response.read()
	response.close()
	
	text_file = open(filename, "w")
	text_file.write(html)
	text_file.close()
	
	
def getPrice(description):
	m = re.findall('(\$\d+)', description, re.MULTILINE)
	if m:
		return m[len(m)-1]
	m = re.findall('([0-9]+\.[0-9][0-9])', description, re.MULTILINE)
	if m:
		return m[len(m)-1]
	return ""

def getSold(description):
	m = re.search(r'\bsold|traded|gifted|unavailable\b', description, re.IGNORECASE)
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


def generateListing(vfm, geeklist, availableFilename, includeSold):
	baseFilename, fileExtension = os.path.splitext(availableFilename)
	allFilename = baseFilename + '_all' + fileExtension

	outFilename = availableFilename if not includeSold else allFilename

	fout = open(outFilename, "w")
	
	fout.write('<html><head><title>' + vfm['title'] + '</title>\n')
	fout.write('<link rel="stylesheet" href="base.css">\n')
	fout.write('<script src="sorttable.js"></script>\n')
	fout.write('</head><body>\n')
	fout.write('<h1><a href="https://boardgamegeek.com/geeklist/' + geeklist + '">'  + vfm['title'] + '</a></h1>\n')
	fout.write('<p><a href="' + availableFilename + '">[Available items only]</a> <a href="' + allFilename + '">[All items]</a></p>\n')
	fout.write('<p></br></p>\n')
	fout.write('<table class="sortable">\n');
	fout.write('<tr><th>Game</th><th>Price</th><th>Seller</th></td>\n');
	for game in vfm['games']:
		if (not includeSold and game['sold']):
			continue
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

	fout.write("</br></br>Page generated with <a href='https://github.com/llopis/bgg-vfm'>bgg-vfm</a></br>\n")

	fout.close()



def generateStaticFiles(vfm, geeklist, outFilename):
	generateListing(vfm, geeklist, outFilename, False)
	generateListing(vfm, geeklist, outFilename, True)
	

def copyStaticContent(outFilename):
	dir = os.path.dirname(outFilename)
	if (os.path.isdir(dir) == False):
		os.mkdir(dir)
	
	scriptPath = os.path.dirname(os.path.realpath(__file__))
	shutil.copy(scriptPath + "/content/base.css", dir)
	shutil.copy(scriptPath + "/content/sorttable.js", dir)

def generateVFM(geeklist, outFilename):
	filename = "geeklist_" + geeklist + ".xml"
	getGeeklist(geeklist, filename)
	
	xmldoc = minidom.parse(filename)

	vfm = parseData(xmldoc)

	copyStaticContent(outFilename)
	generateStaticFiles(vfm, geeklist, outFilename)	
    
if __name__ == '__main__':
    try:
		geeklist = sys.argv[1]
		outFilename = sys.argv[2]
		generateVFM(geeklist, outFilename)
    except IndexError:
        print "Usage: %s <geeklist_id> <filename>" % sys.argv[0]
        raise SystemExit

