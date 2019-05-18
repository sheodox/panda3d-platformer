import sys

from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText


class MenuUI:
    def __init__(self):
        self.font = loader.loadFont('fonts/PressStart2P-Regular.ttf')

    def show_beat_game(self):
        OnscreenText(font=self.font, text='You beat the game!!', scale=0.07)

    def show_main_menu(self, play_fn):
        OnscreenText(font=self.font, text='Panda3D Platformer!', scale=0.1, pos=(0, 0.5, 0), bg=(0, 0, 0, 0), fg=(1, 1, 1, 1))
        DirectButton(text_font=self.font, text='Start', scale=0.12, command=play_fn)
        DirectButton(text_font=self.font, text='Quit', scale=0.12, pos=(0, 0, -0.2), command=sys.exit)

