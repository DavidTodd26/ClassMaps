import sys
from bs4 import BeautifulSoup as Soup
longs = []
lats = []
total = []
def parseLog(file):
    soup = Soup(file, "lxml")
    for message in soup.findAll('longitude'):
        long = message.text
        longs.append(long)
    for message in soup.findAll('latitude'):
        lat = message.text
        lats.append(lat)
    for i in range(len(longs)):
        total.append([longs[i], longs[i]])
    return total
parseLog(xml)