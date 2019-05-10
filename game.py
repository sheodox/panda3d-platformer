from worldgen import WorldGen


class Game:
    def __init__(self, main, level_name):
        self.main = main
        self.world_gen = WorldGen(main, level_name)
        self.level = self.world_gen.get_level()

    def spawn_character(self):
        pass
