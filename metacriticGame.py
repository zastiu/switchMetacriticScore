# -*- coding: utf-8 -*-

import time
import requests
import logging
import os
import tkinter as tk
import tkinter.ttk as ttk
import xml.etree.ElementTree as ET


__author__ = "zastiu"
__version__ = "v0.0.5"

fileOutName = 'z_titleSwitchScore.txt'
fileMetacritic = "z_titleSwitchMetacritic.txt"
titleKeysFile = 'titlekeys.txt'

def get_game_scores(game_to_find,list_games):
    
    for game in list_games:
        if translate_game_name(game[0]) == translate_game_name(game_to_find):
            score = game[1]            
            user_score = game[2]
            return game[1],game[2]
    return "-","-"   


def translate_game_name(game):
    dic = [[":",""], ['.',''], ['"',''], ["&",""], ['&amp;',""], ['&amp;',""], ['(EU)',""], ['[DLC] ',""], ['®',""], ['(CHN/JP/KOR)',""], ['(JP)',""], ['(US/JP)',""], ['(US)',""], ["'",""], ["(AU)",""],['','']]
    game = replace_all(game, dic)
    return game

def replace_all(text, dic):
    for d in dic:
        text = text.replace(d[0], d[1])
    return text

def get_list_of_games():
    list_games = []
    
    page = 0
    last_page = False
    fOutt = open(fileMetacritic, 'w', encoding="utf-8")
    while(last_page == False):
        url = "http://www.metacritic.com/browse/games/score/metascore/all/switch/all?sort=desc&page="+str(page)
        
        html_doc = keep_trying_to_get_html(url)
        cont = html_doc.content

        if str(cont).find("No Results Found")>=0:
            last_page = True
        else:       

            split1 =  str(cont).split('body_wrap">')[1]
            split2 =  split1.split('<div class="post_foot">')[0]
            tree = split2.replace("\\n","").replace("\\t","").replace("  ","").replace("&","&amp;")
            tree = tree[:-12]
           
            parser = ET.XMLParser(encoding="utf-8")
            etree = ET.fromstring(tree, parser)
            for game in etree.findall(".//*[@class='product_row game first']"):
               game_name,game_score,user_score = get_game_info(game)
               list_games.append([game_name,game_score,user_score])
               fOutt.write(game_name+"|"+game_score+"|"+user_score )           
            for game in etree.findall(".//*[@class='product_row game']"):
               game_name,game_score,user_score = get_game_info(game)
               list_games.append([game_name,game_score,user_score])
               fOutt.write(game_name+"|"+game_score+"|"+user_score )
            for game in etree.findall(".//*[@class='product_row game lastt']"):
               game_name,game_score,user_score = get_game_info(game)
               list_games.append([game_name,game_score,user_score])
               fOutt.write(game_name+"|"+game_score+"|"+user_score )
               
        page = page+1
    fOutt.close()
    return list_games
   
def get_game_info(game_element):
    """gameInfo = ET.tostring(game_element, encoding='utf8', method="xml")
    print(gameInfo)"""

    game_score = game_element.find(".//*[@class='product_item product_score']/div").text
    game_name = game_element.find(".//*[@class='product_item product_title']/a").text
    user_score_node = game_element.findall(".//*[@class='product_item product_userscore_txt']/span")
    
    user_score = user_score_node[1].text
    print("Game: ",game_name, " Score: ",game_score, " UserScore: ",user_score)
    if game_score == "tbd":
        game_score = "-"
    if user_score == "tbd":
        user_score = "-"
    return game_name,game_score,user_score   
    
    
def keep_trying_to_get_html(url, attempt=0):
    logging.debug('[keep_trying_to_get_html] Making request to: ' + url)
    try:
        user_agent = {
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        html_doc = requests.get(url, headers=user_agent )
        return html_doc
    except:
        if attempt > 3:
            logging.error("Giving up on HTTP request: " + url)
            raise Exception("Failed to fetch " + url)
        logging.debug('[keep_trying_to_get_html] HTTP error on ' + url + '. Retrying...')
        time.sleep(1)
        print("Try ", attempt)
        return keep_trying_to_get_html(url, attempt=attempt + 1)

class App(tk.Frame):
    def __init__(self, master=None):

        tk.Frame.__init__(self, master)
        self.master = master
        nameApp = "Metacritic Score " + __version__
        root.wm_title(nameApp)

        game_selection_frame = tk.Frame(root)
        game_selection_frame.grid(row=1, column=0, padx=20, pady=20, sticky="N")

        self.scrollbar = tk.Scrollbar(game_selection_frame)
        ##        self.scrollbar.grid(row=1, column=1, sticky=N+S+W)
        self.title_list = tk.Listbox(game_selection_frame, exportselection=False, \
                                  yscrollcommand=self.scrollbar.set, selectmode='extended')
        ##        self.title_list.grid(row=1, column=0, sticky=W)
        self.scrollbar.config(command=self.title_list.yview)

        # Setup Treeview and Two Scrollbars
        container = ttk.Frame(game_selection_frame)
        container.grid(row=1, column=0, columnspan=2)
        self.tree = ttk.Treeview(columns=("num", "G", "S", "US"), show="headings", selectmode='extended')
        self.tree.heading("num", text="#", command=lambda c="num": self.sortby(self.tree, c, 0))
        self.tree.column("num", width=40)
        self.tree.heading("G", text="Game", command=lambda c="G": self.sortby(self.tree, c, 0))
        self.tree.column("G", width=590)
        self.tree.heading("S", text="Score", command=lambda c="S": self.sortby(self.tree, c, 0))
        self.tree.column("S", width=50)
        self.tree.heading("US", text="User Score", command=lambda c="US": self.sortby(self.tree, c, 0))
        self.tree.column("US", width=50)

        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container, columnspan=2)
        vsb.grid(column=2, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        with open(fileOutName, encoding="utf8") as f:
            self.games = f.readlines()
        i= 1
        for game in self.games:
            number = i
            game_name = game.split("|")[0]
            score = game.split("|")[1]
            user_score = game.split("|")[2]
            tree_row = (number, game_name, score, user_score)
            self.tree.insert('', 'end', values=tree_row)
            i = i+1


    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        # if the data to be sorted is numeric change to float
        # data =  change_numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            self.tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        self.tree.heading(col, command=lambda col=col: self.sortby(tree, col, \
                                                                   int(not descending)))

try:
    with open(titleKeysFile, encoding="utf8") as f:
        lines = f.readlines()
except Exception as e:
    print("Error:", e)
    os.system("pause")
    exit()

if not os.path.exists(fileMetacritic) and not os.path.exists(fileOutName):
    print("Creating " + fileMetacritic)    
    list_games = get_list_of_games()
    print("Creating " + fileOutName)
    try:
        fOut = open(fileOutName, 'w', encoding="utf-8")
        for line in lines:
            if line.strip() != '':
                game = line.split("|")[2].replace("\n", "")
                #game_url = "".join([x if ord(x) < 128 else '' for x in game])
                score, user_score = get_game_scores(game, list_games)
                fOut.write(game + "|" + score + "|" + user_score +  "\n")
        fOut.close()
    except Exception as e:
        print("Error:", e)
        os.system("pause")
else:
    print("File "+fileOutName+"and "+fileMetacritic+ " found")  

root = tk.Tk()
app = App(root)
app.grid()
app.mainloop()


