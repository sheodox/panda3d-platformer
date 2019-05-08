from direct.actor.Actor import Actor

from levelparser import LevelParser

class WorldGen:
    def __init__(self, main):
        self.main = main
        self.parser = LevelParser()
        self.main.camera.set_pos(7, -49, 5)

    def load(self, level):
        level = self.parser.load_level_file(level)
        for block in level.blocks:
            self._create_block(block['pos'], block['width'])

    def _create_block(self, pos, width):
        block = self.main.loader.loadModelCopy('models/block')
        block.set_pos(pos)
        block.set_sx(width)
        block.reparent_to(self.main.render)
