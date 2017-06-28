import sys
import pygame as pg

from state_engine import Game, GameState
import prepare
import splash, gameplay

states = {"SPLASH": splash.Splash(),
               "GAMEPLAY": gameplay.Gameplay()}
game = Game(prepare.SCREEN, states, "SPLASH")
game.run()
pg.quit()
sys.exit()