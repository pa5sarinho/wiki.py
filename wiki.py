import requests
import webbrowser
import os
import re
from math import ceil
from bs4 import BeautifulSoup

BASE_URL = "https://en.wikipedia.org/w/index.php?search="

# ANSI code for coloring the terminal characters
CYAN = "\33[0;49;96m"
GRAY = "\33[0;49;90m"
GREEN = "\33[0;49;92m"
YELLOW = "\33[0;49;93m"
FOREGROUND = "\33[0;49;37m"

CYAN_BKG = "\33[7;49;96m"
GRAY_BKG = "\33[7;49;90m"
GREEN_BKG = "\33[7;49;92m"
YELLOW_BKG = "\33[7;49;93m"
FOREGROUND_BKG = "\33[7;49;37m"

# choose your color scheme configuration to best suit your terminal
h1 = YELLOW_BKG
h2 = GREEN_BKG
h3 = CYAN
p = FOREGROUND
a = CYAN

# links = dict()
wikiLogo=['          _ _    _                _ _                        ',
'__      _(_) | _(_)_ __   ___  __| (_) __ _   ___  _ __ __ _ ',
"\\ \\ /\\ / / | |/ / | '_ \ / _ \/ _` | |/ _` | / _ \| '__/ _` |",
' \\ V  V /| |   <| | |_) |  __/ (_| | | (_| || (_) | | | (_| |',
'  \\_/\\_/ |_|_|\\_\\_| .__/ \\___|\\__,_|_|\\__,_(_)___/|_|  \\__, |',
'                  |_|                                  |___/ ']


def getHTML(userInput: str):
    '''Takes a string as an argument. Makes a wikipedia search
    and returns a BeautifulSoup object of the most relevant article'''
    print(p+'\nsearching...')
    html = requests.get(BASE_URL + userInput).text
    return BeautifulSoup(html, 'html.parser')

def printit(soup: BeautifulSoup, fullpage=False):
    '''The optional fullpage argument specifies if it should print the whole
    article with no need of user confirmation'''
    i=0
    page = soup.find_all(['p', 'h1', 'h2', 'h3'])
    terminal_width = os.get_terminal_size()[0]
    number_of_paragraphs = 1
    
    for text in page:
        unformatted_text = page[i].get_text()
        # getting rid of citations and [edit]
        formatted_text = re.sub(r"\[.*?\]", "", unformatted_text)
        if text.name == "p":
            # paragraphs are formatted according to terminal width (columns)
            if len(page[i].get_text()) > terminal_width:
                remaining = 0
                last_bit = 0
                row = 0 # while loop increment
                printed = 0 # keeping track of printed characters

                while True:
                    thisRow = '\n'+formatted_text[(row*terminal_width)-remaining:terminal_width*(row+1)-remaining]

                    if len(thisRow) < terminal_width:
                        index = -1
                    else:
                        # finds the last space in a line under terminal size
                        index = -thisRow[::-1].find(' ')
                        # weird things happen when ' ' is the last character
                        if index == 0:
                            index = -1
                        
                    print(p+thisRow[:index], end='')

                    printed += len(thisRow[:index]) - 1

                    # stores the chars after the space to be added next line
                    remaining += len(thisRow[index:])
                    last_bit = len(thisRow[index:])

                    if printed+last_bit+1 == len(formatted_text):
                        break
                    row += 1
                debug = len(formatted_text)
                print()
            else:
                if formatted_text.strip() != '':        
                    print(p+formatted_text)
                else:
                    number_of_paragraphs -= 1
            number_of_paragraphs += 1

        elif formatted_text.strip() != '':
            #if text.name == 'a':
            #    links[formatted_text] = page[i].get('href') 
            if text.name == 'h1':
                print('\n'+h1+formatted_text.center(terminal_width))
            elif text.name == 'h2' and formatted_text != 'Contents':
                if terminal_width > 50:
                    h2_width = int(terminal_width/4)
                else:
                    h2_width = 20
                print('\n'+h2+formatted_text.rjust(h2_width,'.'))
            elif text.name == 'h3':
                print('\n'+h3+formatted_text)

        # prompts input after 3 paragraphs if fullpage is set to false
        if number_of_paragraphs == 4 and not fullpage:
            confirmation = input(GRAY_BKG+'\n[Enter] shows the whole article | Any character to go back: ')
            if confirmation == '':
                number_of_paragraphs = 6
                pass
            else:
                break
            
        i+=1

def get_page_links(soup: BeautifulSoup): # only the important ones
    a_href = list()
    a_titles = list()
    for tag in soup.find_all(href=re.compile('/wiki')):
        a_titles.append(tag.get_text())
        a_href.append('https://en.wikipedia.org'+tag.get('href'))
    links = zip(a_titles, a_href)
    return dict(links)

def print_links(link_dict):
    i = 0
    for name, link in link_dict:
        if i%3 == 0:
            print() # new line
        print(f'[{i}] {name}', end=' ')
        i += 1

if __name__ == '__main__':
    for line in wikiLogo:
        print(line)
        
    print('Search anything! If a page looks broken, try using different words.\nTo exit, just submit an empty input.')

    while True:
        searchTerm = input(CYAN+'\n> ')
        if searchTerm == '':
            quit()
        elif searchTerm == 'b':
            webbrowser.open(BASE_URL + previous_search)
        else:
            article = getHTML(searchTerm)
            if searchTerm == 'a':
                print_links(get_page_links(article))
            else:
                printit(article)
                previous_search = searchTerm
                print(p+'[b] opens the above page on your default browser')
                print('[a] shows a list of the links')
