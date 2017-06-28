import pygame as pg

import tools, prepare
from state_engine import GameState
from labels import Label


class Splash(GameState):
    def __init__(self):
        super(Splash, self).__init__()
        self.next_state = "GAMEPLAY"
        self.labels = pg.sprite.Group()
        Label("Splash Screen", {"midbottom": prepare.SCREEN_RECT.center},
                 self.labels, font_path=prepare.FONTS["weblysleekuisb"],
                 text_color="gold4", font_size=96)
                 
    def startup(self, persistent):
        self.persist = persistent
        
    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            else:
                self.done = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.done = True
            
    def update(self, dt):
        pass
        
    def draw(self, surface):
        surface.fill(pg.Color("dodgerblue"))
        self.labels.draw(surface)