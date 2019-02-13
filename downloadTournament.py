#!/usr/bin/python
import urllib
import sys
import json
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

if len(sys.argv) != 2:
	print "Please pass an url as an argument"
else:
	url = sys.argv[1]
	html = urllib.urlopen(url).read()
	parsed_html = BeautifulSoup(html, 'html.parser')

	title = parsed_html.h2.string.replace("\n", "")

	decksOdd  = parsed_html.find_all("tr", {"class":"tournament-decklist-odd"})
	decksEven = parsed_html.find_all("tr", {"class":"tournament-decklist-event"})

	decks = []

	exportableJson = {}
	exportableJson['title'] = title
	exportableDecks = []

	for i in range(0,16):
		decks.append(decksOdd[i])
		decks.append(decksEven[i])

	for i in range(0,32):
		print("Adding deck " + str(i+1))
		deck = decks[i]
		exportableDeck = {}
		rows = deck.find_all("td")
		exportableDeck['p'] = i+1
		exportableDeck['w'] = rows[0].string.replace("\n", "")
		exportableDeck['l'] = rows[1].string.replace("\n", "")
		exportableDeck['n'] = rows[2].string.replace("\n", "")
		exportableDeck['pl'] = rows[3].string.replace("\n", "")
		decklistId = rows[6].get("data-deckid")
		decklist = urllib.urlopen("https://www.mtggoldfish.com/deck/download/" + decklistId).read()
		exportableMain = []
		exportableSide = []
		main = 1
		for row in decklist.splitlines():
			if row == "":
				main = 0
			else:
				exportableCard = {}
				exportableCard['q'] = row[:1]
				search = json.loads(urllib.urlopen("https://api.scryfall.com/cards/search?q=!\""+ row[2:] +"\"%22").read())
				exportableCard['id'] = search["data"][0]["oracle_id"]
				if (main == 1):
					exportableMain.append(exportableCard)
				else:
					exportableSide.append(exportableCard)
		exportableDeck['m'] = exportableMain
		exportableDeck['s'] = exportableSide
		exportableDecks.append(exportableDeck)
	exportableJson['decks'] = exportableDecks
	f = open(title + ".json", "w")
	f.write(json.dumps(exportableJson))
	f.close()
	print("Done!")