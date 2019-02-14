#!/usr/bin/python
import urllib
import sys
import json
from time import sleep
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

if len(sys.argv) != 2:
	print "Please pass an url as an argument"
else:

	cardIds = {}
	cardIds['Plains'] = "7a2c8b8e-2e28-4f10-b04f-9b313c60c0bb"
	cardIds['Island'] = "105b2118-b22c-4ef5-bac7-836db4b8b9ee"
	cardIds['Swamp'] = "f108b0fb-420a-422d-ae85-9a99c0f73169"
	cardIds['Mountain'] = "44c1a862-00fc-4e79-a83a-289fef81503a"
	cardIds['Forest'] = "f8772631-d4a1-440d-ac89-ac6659bdc073"

	url = sys.argv[1]
	html = urllib.urlopen(url).read()
	parsed_html = BeautifulSoup(html, 'html.parser')

	title = parsed_html.h2.string.replace("\n", "")
	formatAndDate = parsed_html.h2.parent.find_all("p")[1].get_text().replace("\n", "")

	dateIndex = formatAndDate.index(" Date: ")
	format = formatAndDate[8:dateIndex]
	date = formatAndDate[dateIndex+7:]

	decksOdd  = parsed_html.find_all("tr", {"class":"tournament-decklist-odd"})
	decksEven = parsed_html.find_all("tr", {"class":"tournament-decklist-event"})

	decks = []

	exportableJson = {}
	exportableJson['title'] = title
	exportableDecks = []

	deckSize = len(decksOdd) + len(decksEven)

	for i in range(0,deckSize):
		if (i%2 == 0):
			decks.append(decksEven[i/2])
		else:
			decks.append(decksOdd[(i-1)/2])

	for i in range(0,len(decks)):
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
				sleep(0.05)
				exportableCard = {}
				exportableCard['q'] = row[:row.index(" ")]
				name = row[row.index(" ")+1:]
				if (name in cardIds):
					exportableCard['id'] = cardIds[name]
					print ("We had " + name)
				else:
					search = json.loads(urllib.urlopen("https://api.scryfall.com/cards/search?q=!\""+ name +"\"%22").read())				
					exportableCard['id'] = search["data"][0]["id"]
					cardIds[name] = exportableCard['id']
					print ("We didn't have " + name)
				if (main == 1):
					exportableMain.append(exportableCard)
				else:
					exportableSide.append(exportableCard)
		exportableDeck['m'] = exportableMain
		exportableDeck['s'] = exportableSide
		exportableDecks.append(exportableDeck)
	exportableJson['decks'] = exportableDecks
	f = open(format + "/" + date + ".json", "w")
	f.write(json.dumps(exportableJson))
	f.close()
	print("Done!")