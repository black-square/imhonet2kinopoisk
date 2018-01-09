from enum import Enum, unique
from bs4 import BeautifulSoup
import json
import re
import logging

from utils import Struct


@unique
class Rating(Enum):
    WATCHED = -1
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    R8 = 8
    R9 = 9
    R10 = 10

class ItemInfo(Struct):
    title = None
    year = None
    rating = None
    folders = None

    def snippet(self):
        return f"{self.title} ({self.year})"

    def __repr__(self):
        s = f"{{{self.snippet()}"

        if self.rating:
            s += f" = {self.rating.name}"

        if self.folders:
            s += f" {self.folders}"

        s += "}}"

        return s

def LoadFromHtml(html_doc, extra_links_dict_file):

    if extra_links_dict_file:
        with open(extra_links_dict_file, encoding='UTF8') as fp:
            extraLinks = json.load(fp)
    else:
        extraLinks = {}
            
    with open(html_doc, encoding='UTF8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    res = []

    data = soup.find_all('tr')
    firstTr = soup.table.tbody.tr

    #Skip a ther first header line
    for tr in firstTr.next_siblings:
        td = tr.td
    
        cont = td.contents
        item = ItemInfo()

        title = td.text
        link = extraLinks.get(title)

        if len(cont) == 2:
            fileLink = td.a['href']

            if not link:
                link = fileLink
            else:
                logging.info( "Link %s to '%s' was replaced by %s from the external dictionary", fileLink, title, link )

            item.title = td.a.string
            match = re.match(r"\s*\((\d+)\)", td.contents[1])
            item.year = int(match[1])
        else:
            assert len(cont) == 1

            if not link:
                logging.warning( "Link to '%s' hasn't been found. Use the external dictionary to provide the link.", title )

            match = re.match(r"(.+?)\s*\((\d+)\)", title)
            item.title = match[1]
            item.year = int(match[2])

        td = td.next_sibling

        ratingStr = td.string

        if ratingStr == 'Нет оценки':
            item.rating = Rating.WATCHED
        elif ratingStr == 'Мне интересно':
            item.folders = [0]
        else:
            item.rating = Rating(int(ratingStr))
        
        res.append( (link, item ) )

    return res
