from direct.gui.OnscreenText import OnscreenText


class MenuUI:
    def __init__(self):
        self.font = loader.loadFont('fonts/PressStart2P-Regular.ttf')
        self.center_message_ost = OnscreenText(font=self.font, text="", scale=0.07)

    def show_beat_game(self):
        self.center_message_ost.text = 'You beat the game!!'

