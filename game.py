from worldgen import WorldGen


class Game:
    def __init__(self, main, level_name):
        self.main = main
        self.world_gen = WorldGen(main)
        self.level = self.world_gen.load(level_name)

    def spawn_character(self):
        pass
