import requests
import webbrowser
import os
import re
from math import ceil
from bs4 import BeautifulSoup

BASE_URL = "https://en.wikipedia.org/w/index.php?search="

#save .html files where?
FILE_PATH = '/home/passarinho/notes/html/'

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
h1 = YELLOW
h2 = GREEN
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


def getHTML(userInput: str, saveHTML: bool = False):
    '''Takes a string as an argument. Makes a wikipedia search
    and returns a BeautifulSoup object of the most relevant article.
    if saveHTML is set to True, it saves the html file locally'''
    if not saveHTML:
        print(p+'\nsearching...')
    else:
        print(p+'\nsaving '+userInput+'.html to '+FILE_PATH)
        
    html = requests.get(BASE_URL + userInput).text
    if saveHTML:
        with open(f'{FILE_PATH}{userInput}.html', 'w+') as file:
            file.write(html)
        print('done')
            
    return BeautifulSoup(html, 'html.parser')

def printit(soup: BeautifulSoup, fullpage=False, markdown=False):
    '''The optional fullpage parameter specifies if it should print the whole
    article with no need of user confirmation.'''
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
                print()
                
            else:
                if formatted_text.strip() != '':        
                    print(p+formatted_text)
                else:
                    number_of_paragraphs -= 1
            number_of_paragraphs += 1

        elif formatted_text.strip() != '':
            if text.name == 'h1':
                print('\n'+h1+formatted_text.center(terminal_width, '.'))
            elif text.name == 'h2' and formatted_text != 'Contents' and text != 'See also':
                print('\n'+h2+formatted_text.center(terminal_width, '.'))
            elif text.name == 'h3':
                print('\n'+h3+formatted_text)

        # prompts input after 3 paragraphs if fullpage is set to false
        if number_of_paragraphs == 4 and not fullpage:
            confirmation = input(GRAY+'\n[Enter] shows the whole article | Any character to go back: ')
            if confirmation == '':
                number_of_paragraphs = 6
                pass
            else:
                break
            
        i+=1

def get_page_links(soup: BeautifulSoup):
    '''creates and returns a dictionary in the format {"page title":"page address"}
    in alphabetical order for the soup object given as argument'''
    a_href = list()
    a_titles = list()
    main_content = soup.find('div',attrs={'id':'mw-content-text'})

    for a in main_content.find_all('a'):
        address = a.get('href')
        try:
            if "/wiki/" in address:
                a_titles.append(a.get_text())
                a_href.append('https://en.wikipedia.org'+address)
        except TypeError:
            pass

    links = dict(zip(a_titles, a_href))
    sorted_links = dict(sorted(links.items()))
    return sorted_links

def print_links(link_dict, links_per_row=3):
    i = 0
    for name in link_dict:
        if i % links_per_row == 0:
            print() # new line
        print(f'[{i:<3}] {name:<30}', end=' ')
        i += 1
    
    print('\n\nType a page ID number to view its content\nPress Enter to go back')
    chosenLink = input(CYAN+'\n> ')

    if chosenLink == '':
        print('going back to searching')
    else:
        links = list(link_dict.values())
        html = requests.get(links[int(chosenLink)]).text
        printit(BeautifulSoup(html, 'html.parser'))

if __name__ == '__main__':

    for line in wikiLogo:
        print(line)
        
    print('To exit, just submit an empty input.')
    print('You can type /save before a query to download the article.')

    while True:
        searchTerm = input(CYAN+'\n> ')
        if searchTerm == '':
            quit()
        elif searchTerm == 'b':
            webbrowser.open(BASE_URL + previous_search)
        else:
            if searchTerm == 'a':
                print_links(get_page_links(article))
            elif searchTerm == 'm':
                saveToMarkdown(article)
            else:
                if searchTerm[:5] == '/save':
                    getHTML(searchTerm[6:], saveHTML=True)
                else:
                    article = getHTML(searchTerm)
                    printit(article)
                    previous_search = searchTerm
                    print(p+'\n[a] browse articles mentioned in the page')
                    print('[b] opens the above page on your default browser')
