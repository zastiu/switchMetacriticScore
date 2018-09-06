# -*- coding: utf-8 -*-

import time
import requests
import logging
import os
import tkinter as tk
import tkinter.ttk as ttk
import xml.etree.ElementTree as ET
import platform

__author__ = "zastiu"
__version__ = "v0.1"

fileOutName = 'z_titleSwitch.txt'
titleKeysFile = 'titlekeys.txt'

def get_game_scores(game_to_find, list_games):
    for game in list_games:
        if translate_game_name(game[0]) == translate_game_name(game_to_find):
            score = game[1]
            user_score = game[2]
            return score, user_score
    return "-", "-"

def get_game_times(game_to_find, list_games):
    for game in list_games:
        if translate_game_name(game[0]) == translate_game_name(game_to_find):
            main_story = game[1]
            main_plus_extra = game[2]
            completionist = game[3]
            return main_story, main_plus_extra, completionist
    return "-","-","-"

def translate_game_name(game):
    dic = [[":", ""], ['.', ''], ['"', ''], ["&", ""], ['&amp;', ""], ['&amp;', ""], ['(EU)', ""], ['-', ""], ['®', ""],
           ['™', ""], ['!', ""], ['~', ""], ['(CHN/JP/KOR)', ""], ['FOR NINTENDO SWITCH', ""],
           ['for Nintendo Switch', ""], ['(JP)', ""], ['(US/JP)', ""], ['(US/EU)', ""], ['(US)', ""], ["'", ""],
           ["(AU)", ""], [' ', '']]
    game = replace_all(game, dic)
    return game.lower()


def replace_all(text, dic):
    for d in dic:
        text = text.replace(d[0], d[1])
    return text


def get_list_of_games():
    list_games = []

    page = 0
    last_page = False
    # fOutt = open(fileMetacritic, 'w', encoding="utf-8")
    while (last_page == False):
        url = "http://www.metacritic.com/browse/games/score/metascore/all/switch/all?sort=desc&page=" + str(page)
        html_doc = get_to_html(url)
        cont = html_doc.content
        if str(cont).find("No Results Found") >= 0:
            last_page = True
        else:
            split1 = str(cont).split('body_wrap">')[1]
            split2 = split1.split('<div class="post_foot">')[0]
            tree = split2.replace("\\n", "").replace("\\t", "").replace("  ", "").replace("&", "&amp;")
            tree = tree[:-12]
            parser = ET.XMLParser(encoding="utf-8")
            etree = ET.fromstring(tree, parser)
            for game in etree.findall(".//*[@class='product_row game first']"):
                game_name, game_score, user_score = get_game_info(game)
                list_games.append([game_name, game_score, user_score])
            for game in etree.findall(".//*[@class='product_row game']"):
                game_name, game_score, user_score = get_game_info(game)
                list_games.append([game_name, game_score, user_score])
            for game in etree.findall(".//*[@class='product_row game lastt']"):
                game_name, game_score, user_score = get_game_info(game)
                list_games.append([game_name, game_score, user_score])
        page = page + 1
    return list_games

def get_list_of_games_howlongtobeat():
    list_games = []
    page = 1
    last_page = False


    while (last_page == False):
        url = "https://howlongtobeat.com/search_main.php?page=" + str(page)
        html_doc = post_to_html(url)
        cont = html_doc.content

        if str(cont).find("No results for ") >= 0:
            last_page = True
        else:

            tree = "<root>"+cont.decode("utf-8").replace("&", "&amp;")+"</root>"
            #print("Body:\n", str(tree))
            parser = ET.XMLParser(encoding="utf-8")
            etree = ET.fromstring(tree, parser)


            for game in etree.findall(".//*[@class='back_dark shadow_box']"):
                game_name, main_story, main_plus_extra, completionist = get_game_hltb_info(game)
                list_games.append([game_name,  main_story, main_plus_extra, completionist])
        page = page + 1
    return list_games



def get_game_info(game_element):
    """gameInfo = ET.tostring(game_element, encoding='utf8', method="xml")
    print(gameInfo)"""

    game_score = game_element.find(".//*[@class='product_item product_score']/div").text
    game_name = game_element.find(".//*[@class='product_item product_title']/a").text
    user_score_node = game_element.findall(".//*[@class='product_item product_userscore_txt']/span")

    user_score = user_score_node[1].text
    print("Game: ", game_name, " Score: ", game_score, " UserScore: ", user_score)
    if game_score == "tbd":
        game_score = "-"
    if user_score == "tbd":
        user_score = "-"
    return game_name, game_score, user_score

def get_game_hltb_info(game_element):

    game_name = game_element.find(".//*[@class='text_white']").text
    times = game_element.findall(".//*[@class='search_list_details_block']/div/div")
    if len(times) == 0:
        times = game_element.findall(".//*[@class='search_list_details_block']/div")
    main_story = (times[1].text).replace("&#189;",".5").replace("Hours","").replace(" ","")
    if len(times)>2:
        main_plus_extra = (times[3].text).replace("&#189;",".5").replace("Hours","h").replace(" ","")
        if len(times) > 4:
            completionist = (times[5].text).replace("&#189;",".5").replace("Hours","h").replace(" ","")
        else:
            completionist = "-"
    else:
        main_plus_extra = "-"
        completionist = "-"

    print("Game: ", game_name, " main_story: ", main_story, " main_plus_extra: ", main_plus_extra, " completionist: ", completionist)

    return game_name,  main_story, main_plus_extra, completionist

def get_to_html(url):
    user_agent = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    html_doc = requests.get(url, headers=user_agent)
    return html_doc


def post_to_html(url):
    logging.debug('[keep_trying_to_get_html] Making request to: ' + url)

    headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': '*/*',
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    data = {'queryString': '','t': 'games', 'sorthead': 'popular', 'sortd': 'Normal Order','plat': 'Nintendo Switch',
            'length_type': 'main', 'length_min':'', 'length_max':'', 'detail': ''    }
    payload = "queryString=&t=games&sorthead=popular&sortd=Normal Order&plat=Nintendo Switch&length_type=main&length_min=&length_max=&detail="
    html_doc = requests.post(url, headers=headers, data = payload)
    return html_doc


class App(tk.Frame):
    def __init__(self, master=None):

        global sys_name
        self.listWidth = 67
        sys_name = "Win"

        ##        global save_game_folder
        ##        save_game_folder = False -- To be worked on in the future

        if platform.system() == 'Linux':
            sys_name = "Linux"

        if platform.system() == 'Darwin':
            sys_name = "Mac"
            self.listWidth = 39
        self.sys_name = sys_name

        tk.Frame.__init__(self, master)
        self.master = master
        nameApp = "Metacritic Score " + __version__
        root.wm_title(nameApp)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_list())

        game_selection_frame = tk.Frame(root)
        game_selection_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Filter entrybox
        if sys_name != "Mac":
            entryWidth = self.listWidth + 3
        else:
            entryWidth = self.listWidth
        self.entry = tk.Entry(game_selection_frame, textvariable=self.search_var, width=entryWidth)
        self.entry.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.scrollbar = tk.Scrollbar(game_selection_frame)
        ##        self.scrollbar.grid(row=1, column=1, sticky=N+S+W)
        self.title_list = tk.Listbox(game_selection_frame, exportselection=False, \
                                     yscrollcommand=self.scrollbar.set, selectmode='extended')
        ##        self.title_list.grid(row=1, column=0, sticky=W)
        self.scrollbar.config(command=self.title_list.yview)

        # Setup Treeview and Two Scrollbars
        container = ttk.Frame(game_selection_frame)
        container.grid(row=1, column=0, columnspan=2)
        self.tree = ttk.Treeview(columns=("num", "G", "S", "US", "TM", "TMP", "TC"), show="headings",
                                 selectmode='extended')
        self.tree.heading("num", text="#", command=lambda c="num": self.sortby(self.tree, c, 0))
        self.tree.column("num", width=40)
        self.tree.heading("G", text="Game", command=lambda c="G": self.sortby(self.tree, c, 0))
        self.tree.column("G", width=440)
        self.tree.heading("S", text="Score", command=lambda c="S": self.sortby(self.tree, c, 0))
        self.tree.column("S", width=50)
        self.tree.heading("US", text="User Score", command=lambda c="US": self.sortby(self.tree, c, 0))
        self.tree.column("US", width=50)
        self.tree.heading("TM", text="Main Story", command=lambda c="TM": self.sortby(self.tree, c, 0))
        self.tree.column("TM", width=50)
        self.tree.heading("TMP", text="Main+Extras", command=lambda c="TMP": self.sortby(self.tree, c, 0))
        self.tree.column("TMP", width=50)
        self.tree.heading("TC", text="Completionist", command=lambda c="TC": self.sortby(self.tree, c, 0))
        self.tree.column("TC", width=50)

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
        i = 1
        for game in self.games:
            number = i
            game_name = game.split("|")[0]
            score = game.split("|")[1]
            user_score = game.split("|")[2]
            main_story = game.split("|")[3]
            main_plus_extra = game.split("|")[4]
            completionist = game.split("|")[5]
            tree_row = (number, game_name, score, user_score, main_story, main_plus_extra, completionist)
            self.tree.insert('', 'end', values=tree_row)
            i = i + 1

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

    def update_list(self):

        search_term = self.search_var.get()
        self.tree.delete(*self.tree.get_children())
        i = 1
        for game in self.games:
            number = i
            game_name = game.split("|")[0]
            score = game.split("|")[1]
            user_score = game.split("|")[2]
            main_story = game.split("|")[3]
            main_plus_extra = game.split("|")[4]
            completionist = game.split("|")[5]
            tree_row = (number, game_name, score, user_score, main_story, main_plus_extra, completionist)
            i = i + 1
            if search_term.lower() in game_name.lower():
                self.tree.insert('', 'end', values=tree_row)

        self.tree.yview_moveto(0)
        # Reset the sorting back to default (descending)
        self.tree.heading("num", text="#", command=lambda c="num": self.sortby(self.tree, c, 1))
        self.tree.heading("G", text=("Game"), command=lambda c="G": self.sortby(self.tree, c, 1))
        self.tree.heading("S", text=("Score"), command=lambda c="S": self.sortby(self.tree, c, 1))

        self.tree.heading("TM", text=("Main Story"), command=lambda c="S": self.sortby(self.tree, c, 1))
        self.tree.heading("TMP", text=("Main+Extras"), command=lambda c="S": self.sortby(self.tree, c, 1))
        self.tree.heading("TC", text=("Completionist"), command=lambda c="S": self.sortby(self.tree, c, 1))


try:
    with open(titleKeysFile, encoding="utf8") as f:
        lines = f.readlines()
except Exception as e:
    print("Error:", e)
    os.system("pause")
    exit()

if not os.path.exists(fileOutName):
    print("Getting scores")
    list_games_scores = get_list_of_games()
    print("Getting times")
    list_games_times = get_list_of_games_howlongtobeat()
    print("Creating " + fileOutName)
    try:
        fOut = open(fileOutName, 'w', encoding="utf-8")
        for line in lines:
            if line.strip() != '':
                game = line.split("|")[2].replace("\n", "")
                # game_url = "".join([x if ord(x) < 128 else '' for x in game])
                score, user_score = get_game_scores(game, list_games_scores)
                main_story, main_plus_extra, completionist = get_game_times(game, list_games_times)
                fOut.write(
                    game + "|" + score + "|" + user_score + "|" + main_story + "|" + main_plus_extra + "|" + completionist + "\n")
        fOut.close()
    except Exception as e:
        print("Error:", e)
        os.system("pause")
else:
    print("File " + fileOutName + " found")

root = tk.Tk()
app = App(root)
app.grid()
app.mainloop()
