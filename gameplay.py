from itertools import cycle
from collections import OrderedDict
import json

import pygame as pg

import tools, prepare
from state_engine import GameState
from labels import Label
from sortable_table import SortableTable


def load_nation_data():
    with open("nations_info.json", "r") as f:
        data_dict = json.load(f)
    data_dicts = []
    for k in data_dict:
        d = OrderedDict()
        d["Name"] = k
        d["Population"] = data_dict[k]["population"]
        d["Pop. Growth"] = data_dict[k]["pop growth"]
        d["GDP"] = int(data_dict[k]["gdp"])
        d["GDP Growth"] = data_dict[k]["gdp growth"]
        d["Debt"] = int(data_dict[k]["debt"])
        data_dicts.append(d)
    return data_dicts    


def load_ball_data():
    with open("baseball_info.json", "r") as f:
        data = json.load(f)
    data_dicts = []
    for k in data:
        d = OrderedDict()
        d["Team"] = k
        d["GP"] = data[k]["GP"]
        d["W"] = data[k]["W"]
        d["L"] = data[k]["L"]
        d["SV"] = data[k]["SV"]
        d["R"] = data[k]["R"]
        d["H"] = data[k]["H"]
        d["AVG"] = data[k]["AVG"]
        d["OBP"] = data[k]["OBP"]
        d["AB"] = data[k]["AB"]
        d["ERA"] = data[k]["ERA"]
        d["IP"] = data[k]["IP"]
        d["ER"] = data[k]["ER"]
        d["BB"] = data[k]["BB"]
        data_dicts.append(d)
    return data_dicts

NATION_DATA = load_nation_data()
NATION_FIELD_WIDTHS = [280, 200, 200, 200, 200, 200]
NATION_FIELD_HEIGHT = 24
NATION_HEADER_HEIGHT = 30
NATION_ONSCREEN_RECT = pg.Rect(0, 0, 1280, 720)

NATION_STYLE = {
    "bg_color": "gray90",
    "line_color": "gray40",
    "line_weight": 2,
    "light_field_bg": "gray90",
    "dark_field_bg": "gray 80",
    "field_text_font": prepare.FONTS["weblysleekuisl"],
    "field_text_size": 16,
    "field_text_color": "gray5",
    "header_text_font": prepare.FONTS["weblysleekuisb"],
    "header_text_size": 24,
    "header_text_color": "gray5",
    "field_height": 30,
    "header_height": 48}



BALL_DATA = load_ball_data()
BALL_FIELD_WIDTHS = [150, 50, 50, 50, 50, 50, 50,
                                  80, 80, 80, 80, 80, 80, 80]
BALL_ONSCREEN_RECT = pg.Rect(50, 0, sum(BALL_FIELD_WIDTHS), 400)
BALL_STYLE = {
    "bg_color": "gray90",
    "line_color": "gray40",
    "line_weight": 1,
    "light_field_bg": "gray90",
    "dark_field_bg": "gray 80",
    "field_text_font": prepare.FONTS["weblysleekuisl"],
    "field_text_size": 16,
    "field_text_color": "gray5",
    "header_text_font": prepare.FONTS["weblysleekuisb"],
    "header_text_size": 16,
    "header_text_color": "gray5",
    "field_height": 30,
    "header_height": 48}    
    
class Gameplay(GameState):
    def __init__(self):
        super(Gameplay, self).__init__()
        self.ball_table = SortableTable(BALL_ONSCREEN_RECT,
                                                    BALL_DATA,
                                                    BALL_FIELD_WIDTHS,
                                                    **BALL_STYLE)
        self.nation_table = SortableTable(NATION_ONSCREEN_RECT,
                                                       NATION_DATA,
                                                       NATION_FIELD_WIDTHS,
                                                       **NATION_STYLE)
        self.tables = cycle([self.nation_table, self.ball_table])
        self.table = next(self.tables)
        
    def startup(self, persistent):
        self.persist = persistent

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_t:
                self.table = next(self.tables)            
        self.table.get_event(event)
        
    def update(self, dt):
        mouse_pos = pg.mouse.get_pos()

    def draw(self, surface):
        surface.fill(pg.Color("white"))
        self.table.draw(surface)