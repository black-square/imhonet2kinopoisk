from enum import Enum, unique
from bs4 import BeautifulSoup
import json
import re

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

        if len(cont) == 2:
            link = td.a['href']
            item.title = td.a.string
            match = re.match(r"\s*\((\d+)\)", td.contents[1])
            item.year = int(match[1])
        else:
            assert len(cont) == 1
            title = cont[0]

            link = extraLinks.get(title)

            if not link:
                print( "Link to '{}' hasn't been found. Use external dictionary to provide the link.".format(title) )

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
        
        res.append( (link, vars(item) ) )

    return res
