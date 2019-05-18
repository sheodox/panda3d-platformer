class AI:
    def __init__(self, start_pos):
        self.start_pos = start_pos
        # don't animate or move until they'd otherwise be on screen, don't want AI falling into pits
        # before the player ever sees them
        self.activated = False

    def activate(self):
        self.activated = True
