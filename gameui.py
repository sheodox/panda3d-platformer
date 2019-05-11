from direct.gui.OnscreenText import OnscreenText


class GameUI:
    def __init__(self):
        self.font = loader.loadFont('fonts/PressStart2P-Regular.ttf')
        self.center_message_ost = OnscreenText(font=self.font, text="", scale=0.07)
        self.lives_ost = OnscreenText(font=self.font, scale=0.03, pos=(-0.9, 0.9))
        self.coins_ost = OnscreenText(font=self.font, scale=0.03, pos=(-0.9, 0.85))
        self.time_ost = OnscreenText(font=self.font, scale=0.03, pos=(-0.9, 0.80))

    def show_win(self):
        self.center_message_ost.text = 'You win!'

    def show_lose(self):
        self.center_message_ost.text = 'You lose!'

    def update(self, game_data):
        self.lives_ost.text = f'Lives {game_data["lives"]}'
        self.coins_ost.text = f'Coins {game_data["coins"]}'
        self.time_ost.text = f'Time {game_data["time"]}'

